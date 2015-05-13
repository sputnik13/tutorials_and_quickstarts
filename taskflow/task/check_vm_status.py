# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow import task
import random
from time import sleep


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
            return "allliiiivee allllIIIIIVEEEE aLLLLIIIIVEEEEE!!! %d" % \
                (vm_id)

    def revert(self, vm_id, **kwargs):
        print "VM %d - Check sleeping" % (vm_id)
        sleep(0.1)
