# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

import signal
import sys

from taskflow.jobs import backends as job_backends
from taskflow.persistence import backends as persistence_backends
from taskflow.conductors import single_threaded

PERSISTENCE_BACKEND_CONF = {
    #"connection": "mysql+pymysql://taskflow:taskflow@localhost/taskflow",
    "connection": "zookeeper",
}

JOB_BACKEND_CONF = {
    "board": "zookeeper",
    "path": "/taskflow/jobs/tutorial_conduct",
}


def main():
    with persistence_backends.backend(PERSISTENCE_BACKEND_CONF.copy()) \
            as persistence:

        with job_backends.backend('tutorial_conduct', JOB_BACKEND_CONF.copy(),
                                  persistence=persistence) \
                as board:

            conductor = single_threaded.SingleThreadedConductor(
                "conductor name", board, persistence, engine='serial')

            sighandler = lambda signum, frame: conductor.stop()
            signal.signal(signal.SIGINT, sighandler)
            conductor.run()


if __name__ == "__main__":
    sys.exit(main())
