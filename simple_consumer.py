# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow import engines
from taskflow.patterns import linear_flow
from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow import exceptions as excp
from taskflow import retry

from time import sleep
import sys
import task
import flow

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    "path": "/taskflow/jobs/tutorial_simple",
}


def main():
    vm_flow = flow.create_cluster()

    consumer_name = "Consumer"
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('tutorial_simple', JOB_BACKEND_CONF.copy(),
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
                            engines.run(vm_flow,
                                        store=job.details['store'],
                                        backend=persistence,
                                        book=job.book)
                        except Exception as e:
                            board.abandon(job, consumer_name)
                            print "%s abandoned" % (job)
                            print e
                        else:
                            board.consume(job, consumer_name)
                            #persistence.get_connection().destroy_logbook(
                                #job.book.uuid
                            #)
                            pass

                print "No jobs, sleeping"
                sleep(1)


if __name__ == "__main__":
    sys.exit(main())
