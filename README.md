# redash-datadog
A datadog plug-in for redash. The plug-in has two parts:

- A datadog [agent check](http://docs.datadoghq.com/guides/agent_checks/) that collects redash-related metrics from redash HTTP status endpoint, with metrics including dashboard counts, queries count, query result count, etc.

- `Celery` and `gunicorn` process metrics. It may be useful to monitor the current number of these worker processes.

# Usage
For redash status agent check,

- Copy redash.py to `/etc/dd-agent/checks.d/` 
- Put in the admin api key to redash.yaml.example and copy it to `/etc/dd-agent/conf.d/redash.yaml`.
- Restart dd-agent

For process checks, tune the parameters and copy process.yaml to `/etc/dd-agent/conf.d/`. You can find documentation [here](https://github.com/DataDog/dd-agent/blob/master/conf.d/process.yaml.example). Then restart dd-agent. Now you can add graphs or monitors in the datadog web console. For example, you can search the metric `system.processes.threads` with tag `celery`. 

# Credits
- Thanks for Kevin Martin (Melraidin) for the idea and the code review. 

# References
- http://docs.datadoghq.com/guides/agent_checks/
- http://docs.redash.io/en/latest/usage/maintenance.html#monitoring
- https://github.com/DataDog/dd-agent/blob/master/conf.d/process.yaml.example
