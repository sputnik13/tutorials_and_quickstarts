# -*- coding: utf-8 -*-

__author__ = 'sputnik13'

from taskflow import task


class CreateVm(task.Task):
    def execute(self, vm_id):
        print "VM %d - Creating" % (vm_id)
