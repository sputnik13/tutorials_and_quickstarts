# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow import exceptions as excp

from time import sleep
import sys

PERSISTENCE_BACKEND_CONF = {
    "connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    }

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    }

def main():
    consumer_name = "CLEAR"

    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) as persistence:

        with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(), persistence=persistence) as board:

            while True:
                job_count = 0;
                for job in board.iterjobs(ensure_fresh=True, only_unclaimed=True):
                    try:
                        board.claim(job, consumer_name)
                    except (excp.NotFound, excp.UnclaimableJob):
                        print "%s claim unsuccessful" % (job)
                    else:
                        try:
                            board.consume(job, consumer_name)
                        except Exception as e:
                            board.abandon(job, consumer_name)
                            print "%s abandoned" % (job)
                            print e
                        else:
                            job_count += 1
                print "%d job(s) cleared" % (job_count)
                sleep(1)


if __name__ == "__main__":
    sys.exit(main())
