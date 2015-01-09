# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow import task
from taskflow import engines
from taskflow.patterns import linear_flow
from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow import exceptions as excp
from taskflow import retry

from time import sleep
import sys
import random

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
}


class CreateVm(task.Task):
    def execute(self, vm_id):
        print "VM %d - Creating" % (vm_id)


class CheckVmStatus(task.Task):
    default_provides = 'vm_status'

    def execute(self, vm_id, vm_name):
        print "VM %d - Checking" % (vm_id)
        vm_status = random.choice(['down', 'building', 'booting', 'live'])
        #vm_status = 'live'
        print "VM %d - Status[%s]" % (vm_id, vm_status)
        if vm_status != "live":
            raise Exception("VM %d - Not live yet" % (vm_id))
        else:
            return "allliiiivee allllIIIIIVEEEE aLLLLIIIIVEEEEE!!! %d" % vm_id

    def revert(self, vm_id, **kwargs):
        print "VM %d - Check sleeping" % (vm_id)
        sleep(0.1)


class PrintVmStatus(task.Task):
    def execute(self, vm_id, vm_status):
        print "VM %d - is %s" % (vm_id, vm_status)


def main():
    vm_flow = linear_flow.Flow('creating vm').add(
        CreateVm(),
        linear_flow.Flow('check vm status',
                         retry=retry.Times(attempts=5)).add(CheckVmStatus(provides='vm_status')),
        PrintVmStatus(),
    )

    consumer_name = "Consumer"
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(),
                                  persistence=persistence) \
                as board:

            while True:
                for job in board.iterjobs(ensure_fresh=True,
                                          only_unclaimed=True):
                    print ("%s attempting to claim" % (job))
                    try:
                        board.claim(job, consumer_name)
                    except (excp.NotFound, excp.UnclaimableJob):
                        print "%s claim unsuccessful" % (job)
                    else:
                        try:
                            engines.run(vm_flow, store=job.details['store'])
                        except Exception as e:
                            board.abandon(job, consumer_name)
                            print "%s abandoned" % (job)
                            print e
                        else:
                            board.consume(job, consumer_name)
                            persistence.get_connection().destroy_logbook(
                                job.book.uuid
                            )

                print "No jobs, sleeping"
                sleep(1)


if __name__ == "__main__":
    sys.exit(main())
