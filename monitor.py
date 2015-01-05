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
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) as persistence:

        with job_backends.backend('my-board', JOB_BACKEND_CONF.copy(), persistence=persistence) as board:

            while True:
                job_count = board.job_count
                print "%d outstanding jobs" % (job_count)
                sleep(1)


if __name__ == "__main__":
    sys.exit(main())
