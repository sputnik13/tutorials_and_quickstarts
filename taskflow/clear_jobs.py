# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow import exceptions as excp

from time import sleep
import sys

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper"
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
}


def clear_board(board, persistence):
    consumer_name = "CLEAR"

    job_count = 0
    for job in board.iterjobs(ensure_fresh=True):
        try:
            board.claim(job, consumer_name)
        except (excp.NotFound, excp.UnclaimableJob):
            print "%s claim unsuccessful" % (job)
        else:
            try:
                board.consume(job, consumer_name)
                persistence.get_connection().destroy_logbook(
                    job.book.uuid
                )
            except Exception as e:
                board.abandon(job, consumer_name)
                print "%s abandoned" % (job)
                print e
            else:
                job_count += 1
    return job_count


def main():
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('tutorial_simple',
                                  {"board": "zookeeper",
                                   "path": "/taskflow/jobs/tutorial_simple"},
                                  persistence=persistence) \
                as board_simple:

            with job_backends.backend('tutorial_conduct',
                                      {"board": "zookeeper",
                                       "path": "/taskflow/jobs/tutorial_conduct"},
                                      persistence=persistence) \
                    as board_conduct:

                while True:
                    job_count = 0
                    job_count += clear_board(board_simple, persistence)
                    job_count += clear_board(board_conduct, persistence)
                    print "%d job(s) cleared" % (job_count)
                    sleep(1)


if __name__ == "__main__":
    sys.exit(main())
