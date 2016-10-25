# redash-datadog
A datadog plug-in for redash. The plug-in has three parts:

- A datadog [agent check](http://docs.datadoghq.com/guides/agent_checks/) that collects redash-related metrics from redash HTTP status endpoint, with metrics including dashboard counts, queries count, query result count, etc.

- `Celery` and `gunicorn` process metrics. It may be useful to monitor the current number of these worker processes.

- `Celery` and `gunicorn` process age. The check `ProceeAgeCheck.py` will send the oldest process age to datadog. It may be useful to know how long these processes have been running.

# Usage
For redash status agent check,

- Copy redash.py to `/etc/dd-agent/checks.d/` 
- Put in the admin api key to redash.yaml.example and copy it to `/etc/dd-agent/conf.d/redash.yaml`.
- Restart dd-agent

For process checks, tune the parameters and copy process.yaml to `/etc/dd-agent/conf.d/`. You can find documentation [here](https://github.com/DataDog/dd-agent/blob/master/conf.d/process.yaml.example). Then restart dd-agent. Now you can add graphs or monitors in the datadog web console. For example, you can search the metric `system.processes.threads` with tag `celery`. 

For process age checks, copy `ProcessAgeCheck.py` and `check_proc_age.sh` to `/etc/dd-agent/checks.d/` and yaml to the `conf.d/` path. Restart dd-agent.

# Credits
- Thanks for Kevin Martin (Melraidin) for the idea and the code review. 

# References
- http://docs.datadoghq.com/guides/agent_checks/
- http://docs.redash.io/en/latest/usage/maintenance.html#monitoring
- https://github.com/DataDog/dd-agent/blob/master/conf.d/process.yaml.example
