[TaskFlow](http://docs.openstack.org/developer/taskflow/) Tutorial
====

See https://wiki.openstack.org/wiki/TaskFlow and http://docs.openstack.org/developer/taskflow/ for official documentation.

See [tutorial.md](https://github.com/sputnik13/taskflow_tutorial/blob/master/tutorial.md) for a high level walkthrough of TaskFlow.


Running example(s)
----

 1. Install and run Zookeeper on localhost
 2. Install Python packages in requirements.txt

Once the running environment is ready use the following scripts to run through the examples:
 - monitor.py - prints a count of outstanding Jobs in the Jobboard
 - clear_jobs.py - clears all outstanding Jobs from the Jobboard
 - simple_producer.py - Adds new Jobs for simple_consumer to consume
 - simple_consumer.py - Consumes Jobs from simple_producer
 - conduct_producer.py - Adds new Jobs for conduct_consumer to consume
 - conduct_consumer.py - Consumes Jobs from conduct_producer
