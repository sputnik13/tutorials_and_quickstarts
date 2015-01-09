# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

import sys
import logging

#logging.basicConfig(level=logging.DEBUG)

from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow.conductors import single_threaded

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
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


if __name__ == "__main__":
    sys.exit(main())
