
Running ad-hoc tasks
-----------------------
    ansible <host-pattern> [-m module_name] [-a args]

When a module is not specified, command module is assumed.  The command module takes args and runs as a CLI command. An inventory is required to provide a mapping to actual hosts from host-pattern. /etc/ansible/inventory.ini is assumed unless explicitly specified by --inventory-file=<file>

  Full list of modules available at [docs.ansible.com][1]


Playbook
--------

	ansible-playbook <playbook>

Playbooks are written in [YAML][2].

**YAML**

	# This is a comment
	
	# Three dashes separate directives from document content
	# and is also used to start a document
	---
	# Collection (list)
     - RabbitMQ
     - ActiveMQ
     - Kafka
     - Redis
	
	# Mapping (dictionary)
	name: Cue
	job: 'Create and manage broker clusters'
	status: 'Too awesome for words'

    # Mapping of List of Mappings
    team:
	    - nick: vipuls
	      role: 'fearless leader'
	    - name: sputnik13
	      role: 'master of scrums'

The python equivalent of the above would be:

	# Collection (list)
	['RabbitMQ',
     'ActiveMQ',
     'Kafka',
     'Redis']
	
	# Mapping (dictionary)
	{ 'name': 'Cue',
	  'job': 'Create and manage broker clusters',
	  'status': 'Too awesome for words' }

    # Mapping of List of Mappings
    { team: [
	    {nick: 'vipuls',
	     role: 'fearless leader' },
	    {name: 'sputnik13',
	     role: 'master of scrums' }]}

A playbook is composed of a list of plays.  A play has the following general form, <...> indicates fields:

	- hosts: <host-pattern>
	  vars:
	      <var1>: <var1_value>
	      <var2>: <var2_value>
	  ...
	  tasks:
		  - name: Some unique name
		    # Either of the following forms is valid
			<module1>: <arg1>=<arg1_value> <arg2>=<arg2_value>
		  - name: Some unique name
		    # Either of the following forms is valid
			<module2>:
				arg1: arg1_value
				arg2: arg2_value
			notify:
				- Handler name
	  ...
	  handlers:
		  - name: Handler name
		    <module>: <arg1>=<arg1_value> <arg2>=<arg2_value>
	  ...
	  <other play options>...

[More play options][3]

**Tasks vs Handlers**
Tasks and Handlers both execute an action using a module.

Tasks are always executed unless a [condition][4] is specified.
Handlers are only executed when notified by a task.  Notifications are triggered only when there is a change in the task that the notification is specified in.

Handlers are normally executed after all tasks to ensure that a handler is executed once per playbook run.  Handlers can also be forced to execute inline to tasks by using a meta statement:

	- meta: flush_handlers

**Conditionals and Loops**
Ansible playbooks support [conditional][4] execution of tasks and [looping][5] to allow more complex playbooks to be created.

**Variables: Passing and Sharing information**
Variables can be defined in the [Inventory](https://docs.ansible.com/playbooks_variables.html#variables-defined-in-inventory), [Playbook](https://docs.ansible.com/playbooks_variables.html#variables-defined-in-a-playbook), or in [included files and roles](https://docs.ansible.com/playbooks_variables.html#variables-defined-from-included-files-and-roles).  Variables can also be defined when executing a play or playbook using the *-e variable=value* option.

	ansible-playbook -e var=val playbook.yaml

Variables provide a means to write playbooks that are agnostic to specific environment settings (IP addresses, database username/password, etc) and provide those values at run-time.

[Facts](https://docs.ansible.com/playbooks_variables.html#information-discovered-from-systems-facts) are variables that are provided by Ansible.  An easy way to discover all available facts is to use the setup module in an ad-hoc ansible command

	ansible <host-pattern> -m setup

Variables also provide tasks a means to communicate state and other information between each other.  [Registered variables](https://docs.ansible.com/playbooks_variables.html#registered-variables) are created using the register option

	# tasks.yaml
	---
    - name: ensure ntpd is at the latest version
      apt: name=ntp state=present
      register: ntpinstalled

The example above stores information about the task execution in a registered variable named *ntpinstalled*

**Code Reuse and Include directive**
Include directives can be used to include one YAML file in another YAML file.

	# tasks.yaml
	---
	- name: ensure ntpd is at the latest version
	  apt: name=ntp state=present
	  register: ntpinstalled
	
	- template:
	    src: ntp.conf.j2
	    dest: /etc/ntp.conf
	  notify:
	  - restart ntp
	
	- name: start ntp
	  when: ntpinstalled|success
	  service: name=ntp state=started

	# handlers.yaml
	---
    - name: restart ntp
      service: name=ntp state=restarted


	# playbook.yaml
	---
    - hosts: all
      vars:
        ntp_server: us.pool.ntp.org
      tasks:
	    - include: tasks.yaml
	
	  handlers:
	    - include: handlers.yaml

**Parameterized Include**
Include directives can pass parameters to the included file.  The parameters are used as variables in the included file.

	# tasks.yaml
	---
	- name: ensure ntpd is at the latest version
	  apt: name=ntp state=present
	  register: ntpinstalled
	
	- template:
	    src: ntp.conf.j2
	    dest: /etc/ntp.conf
	  notify:
	  - restart ntp
	
	- name: start ntp
	  when: ntpinstalled|success
	  service: name=ntp state={{STATE}}

	# handlers.yaml
	---
    - name: restart ntp
      service: name=ntp state={{STATE}}


	# playbook.yaml
	---
	- hosts: all
	  vars:
	    ntp_server: us.pool.ntp.org
	  tasks:
	    - include: tasks.yaml
	      STATE: started
	
	  handlers:
	    - include: handlers.yaml STATE=restarted

Roles
-----
Roles are an automation around 'include' directives, that load vars, tasks, and handlers according to a [well known file structure][6].

Variables
---------
[Variable names][7] always start with a letter, and consist of letters, numbers, and underscores.

Variables are dereferenced in templates, playbooks, included YAML files, etc using {{...}} according to [Jinja2][8] syntax.  Ansible supports the full Jinja2 template language.

[Best Practices](https://docs.ansible.com/playbooks_best_practices.html)
--------------

[1]: http://docs.ansible.com/modules_by_category.html
[2]: http://yaml.org
[3]: http://docs.ansible.com/playbooks_intro.html#basics
[4]: http://docs.ansible.com/playbooks_conditionals.html
[5]: http://docs.ansible.com/playbooks_loops.html
[6]: http://docs.ansible.com/playbooks_roles.html#roles
[7]: http://docs.ansible.com/playbooks_variables.html#what-makes-a-valid-variable-name
[8]: http://jinja.pocoo.org