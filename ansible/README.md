
Running ad-hoc tasks
-----------------------
    ansible <host-pattern> [-m module_name] [-a args]

When a module is not specified, command module is assumed.  The command module takes args and runs as a CLI command. An inventory is required to provide a mapping to actual hosts from host-pattern. /etc/ansible/inventory.ini is assumed unless explicitly specified by --inventory-file=<file>

  Full list of modules available at [docs.ansible.com][1]


Playbook
--------
Playbooks written in YAML.

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

[More play options][2]

**Tasks vs Handlers**
Tasks and Handlers both execute an action using a module.

Tasks are always executed unless a [condition][3] is specified.
Handlers are only executed when notified by a task.  Notification only happens only when there is a change.

**Conditionals and Loops**
Ansible playbooks support [conditional][3] execution of tasks and [looping][4] to allow more complex playbooks to be created.

**Code Reuse and Include directive**
Include directives can be used to include one YAML file in another YAML file.

	# tasks.yaml
	---
    - name: ensure ntpd is at the latest version
      apt: name=ntp state=present
      register: ntpinstalled
      notify:
      - restart ntp
     
    - name: start ntp
      when: ntpinstalled|success
      service: name=ntp state=started

    - name: stop ntp
      when: ntpinstalled|failed
      service: name=ntp state=stopped


	# handlers.yaml
	---
    - name: restart ntp
      service: name=ntp state=restarted


	# playbook.yaml
	---
    - hosts: all
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
      notify:
      - restart ntp
     
    - name: start ntp
      when: ntpinstalled|success
      service: name=ntp state={{STATE}}

    - name: stop ntp
      when: ntpinstalled|failed
      service: name=ntp state=stopped


	# handlers.yaml
	---
    - name: restart ntp
      service: name=ntp state={{STATE}}


	# playbook.yaml
	---
    - hosts: all
      tasks:
	    - include: tasks.yaml
	      STATE: started
	
	  handlers:
	    - include: handlers.yaml STATE=restarted


Roles
-----
Roles are an automation around 'include' directives, that load vars, tasks, and handlers according to a [well known file structure][5].

Variables
---------
[Variable names][6] always start with a letter, and consist of letters, numbers, and underscores.

Variables are dereferenced in templates, playbooks, included YAML files, etc using {{...}} according to [Jinja2][7] syntax.  Ansible supports the full Jinja2 template language.

Facts
-----

[Best Practices](https://docs.ansible.com/playbooks_best_practices.html)
--------------

[1]: http://docs.ansible.com/modules_by_category.html
[2]: http://docs.ansible.com/playbooks_intro.html#basics
[3]: http://docs.ansible.com/playbooks_conditionals.html
[4]: http://docs.ansible.com/playbooks_loops.html
[5]: http://docs.ansible.com/playbooks_roles.html#roles
[6]: http://docs.ansible.com/playbooks_variables.html#what-makes-a-valid-variable-name
[7]: http://jinja.pocoo.org