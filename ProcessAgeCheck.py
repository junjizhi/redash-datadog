#!/usr/bin/env python

# This script checks the process age.
# TODO It is a hack that makes use of the nagios check shell script: check_proc_age.sh.

import subprocess
import time

from hashlib import md5
from checks import AgentCheck

class ProcessAgeCheck(AgentCheck):
    PROCESS_AGE_CHECK_SCRIPT_PATH = "/etc/dd-agent/checks.d/check_proc_age.sh"

    STATUS_MAP = {
        'OK':AgentCheck.OK,
        'WARNING':AgentCheck.WARNING,
        'CRITICAL':AgentCheck.CRITICAL,
        'NO_PROC':AgentCheck.UNKNOWN
    }
    
    def check(self, instance):
        if 'process_name' not in instance:
            self.log.info("Skipping instance, no process_name found.")
            return

        process_name = instance['process_name']
        warning_threshold = instance['warning_threshold']
        critical_threshold = instance['critical_threshold']

        # Use a hash of the all parameters as an aggregation key
        params = "%s,%d,%d"%(process_name, warning_threshold, critical_threshold)
        aggregation_key = md5(params).hexdigest()
        
        # check process age
        try:
            cmd = [self.PROCESS_AGE_CHECK_SCRIPT_PATH, "-p", process_name, "-w", str(warning_threshold), "-c", str(critical_threshold), ]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()

            for line in out.split("\n"):
                splits = line.split(":")
                status_str = splits[0]
                status = self.STATUS_MAP[status_str]
                nProc = int(splits[1])
                maxage = float(splits[2]) / (24 * 60 * 60)

                if status != AgentCheck.UNKNOWN:  # only emit when there is data for the data
                    self.service_check("redash.oldest.%s.process.age"%process_name, status, "%s: there are %d process %s, oldest has got %.4f days age"%(status_str, nProc, process_name, maxage))
                    self.gauge("redash.oldest.%s.process.age"%process_name, maxage)
                break

        except Exception, e:
            self.check_failed_event(process_name, "exception: %s"%str(e), aggregation_key)
                
    def check_failed_event(self, process_name, message, aggregation_key):
        self.event({
            'timestamp':  int(time.time()),
            'event_type': "redash_%s_process_age_check" % (process_name),
            'msg_title':  "redash_%s_process_age_check" % (process_name),
            'msg_text':   message,
            'aggregation_key': aggregation_key
        })

    if __name__ == '__main__':
        check, instances = ProcessAgeCheck.from_yaml('/etc/dd-agent/conf.d/ProcessAgeCheck.yaml')
        for instance in instances:
            print "\nRunning the age check against process: %s" % (instance['process_name'])
            check.check(instance)
            if check.has_events():
                print 'Events: %s' % (check.get_events())
            print 'Metrics: %s' % (check.get_metrics())
