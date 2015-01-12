High Level Overview
-------
A complete TaskFlow "stack" includes one or more of the following:
 - Flow
 - Job
 - Jobboard
 - Job Producer
 - Job Consumer

A Flow is what defines the overall workflow and is composed of one or more Tasks and sub-Flows.  A Task is a step in the overall workflow and performs a small set of actions.  When one or more Tasks are arranged in to a Flow, TaskFlow allows a dependency pattern to be specified, which affects the order and timing in which each Task is executed.

Once a Flow has been defined, Job Producers create one or more Jobs and post Jobs to a Jobboard.  Job Consumers claim ownership of a Job from a Jobboard and executes the Job.

In Object Oriented terms a Flow might be viewed as a Class and a Job as an Object instantiation of the Flow.  More precisely, a Job in TaskFlow is a set consisting of a Job ID, some Job specific parameters, and reference to a "logbook".  The Job is not a specific instantiation of a Flow, rather the Job provides the Job Consumer sufficient information to determine which Flow is to be executed, along with initial parameters for the Flow.

Flow
-------
A Flow is created in a declarative manner and starts with definition of a Task.

	from taskflow import task
	
    class Task1(task.Task):
	    def execute(self, param1):
		    print param1


	class Task2(task.Task):
		def execute(self, param2):
			print param2


Each Task is defined as a sub-class of *taskflow.task.Task* and must implement an *execute* method.  A Task requiring input parameters can specify the parameters by name in the *execute* method.  Although the examples above use a single parameter in each Task, multiple parameters can be specified as necessary.

Once Tasks have been defined, they can be composed in to a Flow.

	from taskflow.patterns import linear_flow

	vm_flow = linear_flow.Flow('creating vm').add(
		Task1(),
		Task2(),
	)

***Note***: It is important that Tasks be as small as possible to take full advantage of TaskFlow.  TaskFlow will record progress of each Task in a Flow, but it provides no facility for storing local variables from within a Task.  Thus, a long and complicated Task that fails at a midpoint will need retry/reversion logic that is able to determine at which point the Task failed and take appropriate action.  Tasks should ideally be idempotent and provide the ability to revert/rollback any changes made by the Task.

The example flow above executes two tasks in a linear pattern.  TaskFlow allows flows to be nested within other flows as sub-Flows.  There are (as of 1/5/2015) three (3) "flow patterns" provided by TaskFlow.

 - **Linear** - treats each task or sub-Flow in a strictly ordered manner, order is dictated by which task or sub-Flow is added first
 - **Unordered** - executes each task or sub-Flow as being independent to other tasks or sub-Flows
 - **Graph** - executes each task or sub-Flow according to a graph relationship (links) defined in the flow

Job, Jobboard, and Job Producer
-------
A Jobboard is a combination of a Job backend and a Persistence backend.  A Jobboard is both created and retrieved from a supported backend with the same function *taskflow.jobs.backends.backend(...)*.

	from taskflow.jobs import backends as job_backends
	from taskflow.persistence import backends as persistence_backends
	from taskflow.persistence import logbook
	...

	PERSISTENCE_BACKEND_CONF = {
		"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
	}
	
	JOB_BACKEND_CONF = {
		"board": "zookeeper",
	}
	...
	
	with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) as persistence:

		with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(), persistence=persistence) as board:
			...

			job_logbook = logbook.LogBook("job name")
			persistence.get_connection().save_logbook(job_logbook)
			job_details = {
				...
			}
			job = board.post("job name", book=job_logbook, details=job_details)

The example above uses a MySQL Persistence backend and a Zookeeper Job backend.  Other Persistence backends are available as well (Memory, Files, Zookeeper, Postgres, and SQLite).

When posting a Job to a Jobboard, the Job Producer creates a dictionary containing "job details", to be submitted with the Job to the Jobboard.  The "job details" need to include all required information for the Job Consumer to select the appropriate Flow and execute the Job.

***Note***: When using Conductors as Job Consumers, input data for Flows are communicated from the Job Producer to the Conductor via the 'store' attribute in the job detail dictionary.  Conductors will be discussed in a later section.

A logbook can optionally be pre-created and posted with the job.  If a logbook is not provided, TaskFlow will automatically create one to track progress.  However, in the event of a failure that results in the Job being reverted, the auto-created logbook will not be reused in subsequent executions of the Job.

***Note***: It is recommended that a pre-created logbook be used with a Job.  Having all flow execution attempts logged under a single logbook will make it easier to perform analysis on the overall behavior of the system.  With auto-generated logbooks for each Job execution attempt, the overall metrics on Job count and throughput will be artificially inflated.

***Note***: Logbooks will not be automatically deleted. Either the Job Consumer or some sort of cleanup process needs to delete logbooks that are no longer needed.

Job Consumer and Job Execution	
-------
A Job Consumer checks a Jobboard for available Jobs.  When an available Job is found, the Job Consumer claims the Job and executes it.  It uses "job details" provided by the Job Producer to determine what Flow to create and execute.

	from taskflow import task
	from taskflow import engines
	from taskflow.patterns import linear_flow
	from taskflow.jobs import backends as job_backends
	from taskflow.persistence import backends as persistence_backends
	from taskflow import exceptions as excp
	...

	PERSISTENCE_BACKEND_CONF = {
		"connection": "zookeeper",
	}
	
	JOB_BACKEND_CONF = {
		"board": "zookeeper",
	}

	with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
			as persistence:

		with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(),
								  persistence=persistence) \
				as board:

			while True:
				# 1. Check Jobboard for unclaimed Jobs
				for job in board.iterjobs(ensure_fresh=True,
										  only_unclaimed=True):
					print ("%s attempting to claim" % (job))
					try:
						# 2. Attempt to claim the first unclaimed Job
						board.claim(job, consumer_name)
					except (excp.NotFound, excp.UnclaimableJob):
						print "%s claim unsuccessful" % (job)
					else:
						try:
							# 3. Determine what flow to use and retrieve it
							#    get_flow_from_details is assumed to be
							#    provided elsewhere
							flow = get_flow_from_details(job)
							
							# 4. Run the Flow with information provided by
							#    the Job
							engines.run(flow,
										store=job.details['store'],
										backend=persistence,
										book=job.book)
						except Exception as e:
							# 5. In the event of a failure, abandon the Job
							board.abandon(job, consumer_name)
							print "%s abandoned" % (job)
							print e
						else:
							# 6. The Flow succeeded, so consume the Job
							board.consume(job, consumer_name)
							
							# 7. Destroy the associated Logbook
							persistence.get_connection().destroy_logbook(
								job.book.uuid
							)

				print "No jobs, sleeping"
				sleep(1)


In the example above the Job Consumer does the following:

 1. Check the Jobboard for unclaimed Jobs
 2. Attempt to claim the first unclaimed Job
 3. Once a Job is claimed, determine what Flow to run
 4. Run the Flow with information provided by the Job
 5. In the event of a failure while running the flow, abandon/release the Job for retry at a later time
 6. Once the Flow completes "consume" the Job
 7. Destroy the Logbook associated with the Job - this is optional and should be done only if maintaining history is not a requirement

Providing Input Data to Tasks	
-------
Tasks can [optionally] take input parameters as part of the execute method.  These parameters are provided in one of two ways.

 - Providing a 'store' argument to the Engine
 - Binding return values from other Tasks to a name

The 'store' argument in the Engine (whether via the *engines.run* or the *engines.load* method) takes a dictionary whose keys correspond to input parameter names.  The dictionary values are available to all sub-Flows and Tasks that make up the Flow being run.  In the Job Producer/Consumer example above, the Job Producer provides the 'store' dictionary as part of the Job's *job_detail* attribute.  The Job Consumer then uses the 'store' dictionary as input to the *engines.load(...)* or *engines.run(...)* method.

It's also possible to bind return values from Tasks to names.  These names are mapped to parameter names in a Task's execute method.  The mapping is done using either the *default_provides* member variable in a Task, or by specifying a value in the *provides* argument.

	from taskflow import task
	from taskflow.patterns import linear_flow
	
    class Task1(task.Task):
	    def execute(self):
		    return "new parameter"


	class Task2(task.Task):
		def execute(self, param2):
			print param2


	flow = linear_flow.Flow('flow name').add(
		Task1(provides='param2'),
		Task2(),
	)

The example above binds the return value from *Task1.execute(...)* to the name 'param2'.  *Task2.execute(...)* expects an argument named 'param2', therefore TaskFlow provides the value of 'param2' from Task1 to Task2 as 'param2'.

***Note***: While the two methods are not mutually exclusive, values provided to the Engine via the 'store' dictionary does take precedence over any named values provided by Tasks.  For example:

	>>> from taskflow import engines
	>>> engines.run(flow)
	new parameter
	{'param2': 'new parameter'}
	>>> engines.run(flow, store={'param2': "override Task1"})
	override Task1
	{'param2': ['override Task1', 'new parameter']}

Handling Errors	
-------
TaskFlow provides facilities for retrying and reverting Tasks and Flows when an error is detected.

Tasks can be reverted while Flows can be retried.  A failure in a Task that results in the Task raising and Exception causes all Tasks and sub-Flows associated to be reverted unless there is a Retry controller defined for Flow/sub-Flow that contains the failed Task.

	from taskflow import task
	from taskflow.patterns import linear_flow
	from taskflow import retry
	from taskflow import engines
	
    class Task1(task.Task):
	    def execute(self):
		    print "Task1"

		def revert(self, **kwargs):
			print "Task1 revert"


	class Task2(task.Task):
		count = 0
		
		def execute(self):
			print "Task2 attempt #%d" % (self.count)
			self.count += 1

		def revert(self, **kwargs):
			print "Task2 revert"


	class BadTask(task.Task):
		def execute(self):
			raise Exception("BadTask")


	flow = linear_flow.Flow('outer flow').add(
		Task1(),
		linear_flow.Flow('inner flow',
						 retry=retry.Times(attempts=5)
						 ).add(Task2(), BadTask())
	)


Running the flow above will result in the following output

	>>> engines.run(flow)
	Task1
	Task2 attempt #0
	Task2 revert
	Task2 attempt #1
	Task2 revert
	Task2 attempt #2
	Task2 revert
	Task2 attempt #3
	Task2 revert
	Task2 attempt #4
	Task2 revert
	Task1 revert
	Traceback (most recent call last):
	  ...
	Exception: BadTask
	>>>

As the example shows, Task1, which is part of the "outer flow" executes once.  When BadTask, which is part of the "inner flow", throws an Exception it triggers a revert of all Tasks that are part of the immediately surrounding Flow (in this case the "inner flow").

Due to the fact that a Retry was defined for the "inner flow", rather than propagating the Exception immediately to the "outer flow" (which would cause an immediate revert of all other Tasks and Flows that are part of the "outer flow"), the "inner flow" is in fact retried up to the defined number of retry intervals (in this case 5).

After the number of retries have been exhausted, the "inner flow" also fails and propagates the Exception up to the "outer flow", which causes Task1 to then revert.

Conductors
-------
A Conductor is a complex Job Consumer provided as an "out of the box" solution by TaskFlow.  A Conductor:

 - Interfaces with a Jobboard to grab new Jobs
 - Creates Engines from the claimed Jobs
 - Runs the Job in the created Engine

Using a Conductor requires a change in behavior from the Job Producer.  Whereas in the examples above the Job Consumer determined what Flow to create based on information provided by the Job Producer (via job_details), a Conductor expects the Job Producer to provide a reference to a factory function, which will create the appropriate Flow for the Job.

**Producer**

	from taskflow.jobs import backends as job_backends
	from taskflow.persistence import backends as persistence_backends
	from taskflow.persistence import logbook
	...

	PERSISTENCE_BACKEND_CONF = {
		"connection": "zookeeper",
	}
	
	JOB_BACKEND_CONF = {
		"board": "zookeeper",
	}
	...
	
	with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) as persistence:

		with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(), persistence=persistence) as board:
			...

			job_logbook = logbook.LogBook("job name")
			flow_detail = logbook.FlowDetail("flow name")
			factory_args = ()
			factory_kwargs = {}
			engines.save_factory_details(flow_detail, create_flow,
										 factory_args, factory_kwargs)
			job_logbook.add(flow_detail)
			persistence.get_connection().save_logbook(job_logbook)
			job_details = {
				...
			}
			job = board.post("job name", book=job_logbook, details=job_details)


Here the key difference is the explicit creation of a FlowDetail by the Producer, which is then populated with "factory_details" using *[engines.save_factory_details(...)](http://docs.openstack.org/developer/taskflow/engines.html#taskflow.engines.helpers.save_factory_details)*.  This method takes the flow_detail to be populated, a flow factory function, a tuple of arguments for the factory function, and a dictionary of kwargs for the factory function.


**Consumer**

	import sys
	from taskflow.jobs import backends as job_backends
	from taskflow.persistence import backends as persistence_backends
	from taskflow.conductors import single_threaded
	
	PERSISTENCE_BACKEND_CONF = {
		"connection": "zookeeper",
	}
	
	JOB_BACKEND_CONF = {
		"board": "zookeeper",
	}
	
	
	def main():
		with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
				as persistence:
	
			with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(),
									  persistence=persistence) \
					as board:
	
				conductor = single_threaded.SingleThreadedConductor(
					"conductor name", board, persistence, engine='serial')
	
				conductor.run()


The above Conductor based Consumer is capable of running any Jobs that are posted to the Jobboard it is connected to.  The caveat is that the Task and Flow code need to be in the Consumer's PYTHONPATH as TaskFlow uses information provided in the Job's FlowDetail to load the code for requisite Flows and Tasks.