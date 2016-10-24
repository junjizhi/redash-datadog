#!/usr/bin/env python

# This is a datadog plug-in to perform checks on redash status endpoint.
# The code below is adapted from http://docs.datadoghq.com/guides/agent_checks/#putting-it-all-together
# The original check script only emits the http response time, or reports timeout event.
# This script adds the parsing of the http response and emits the redash-specific metrics.

import time
import requests

from checks import AgentCheck
from hashlib import md5

class HTTPCheck(AgentCheck):
    def check(self, instance):
        if 'url' not in instance:
            self.log.info("Skipping instance, no url found.")
            return

        # Load values from the instance config
        url = instance['url']
        default_timeout = self.init_config.get('default_timeout', 5)
        timeout = float(instance.get('timeout', default_timeout))

        # Use a hash of the URL as an aggregation key
        aggregation_key = md5(url).hexdigest()

        # Check the URL
        start_time = time.time()
        try:
            r = requests.get(url, timeout=timeout)
            end_time = time.time()            
        except requests.exceptions.Timeout as e:
            # If there's a timeout
            self.timeout_event(url, timeout, aggregation_key)
            return

        if r.status_code != 200:
            self.status_code_event(url, r, aggregation_key)
        else:
            response_json = r.json()
            self.gauge('redash_dashboards_count', response_json["dashboards_count"])
            self.gauge('redash_queries_count', response_json["queries_count"])
            self.gauge('redash_query_results_count', response_json["query_results_count"])
            self.gauge('redash_redis_used_memory', response_json["redis_used_memory"])
            self.gauge('redash_manager_outdated_queries_count', response_json["manager"]["outdated_queries_count"])

        timing = end_time - start_time
        self.gauge('redash_endpoint.reponse_time', timing, tags=['redash_endpoint_check'])

    def timeout_event(self, url, timeout, aggregation_key):
        self.event({
            'timestamp': int(time.time()),
            'event_type': 'redash_endpoint_check',
            'msg_title': 'redash endpoint timeout',
            'msg_text': '%s timed out after %s seconds.' % (url, timeout),
            'aggregation_key': aggregation_key
        })

    def status_code_event(self, url, r, aggregation_key):
        self.event({
            'timestamp': int(time.time()),
            'event_type': 'redash_endpoint_check',
            'msg_title': 'Invalid reponse code for %s' % url,
            'msg_text': '%s returned a status of %s' % (url, r.status_code),
            'aggregation_key': aggregation_key
        })

    if __name__ == '__main__':
        check, instances = HTTPCheck.from_yaml('/etc/dd-agent/conf.d/redash.yaml')
        for instance in instances:
            print "\nRunning the check against url: %s" % (instance['url'])
            check.check(instance)
            if check.has_events():
                print 'Events: %s' % (check.get_events())
            print 'Metrics: %s' % (check.get_metrics())
