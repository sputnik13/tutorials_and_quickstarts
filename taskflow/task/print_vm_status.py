from taskflow import task


class PrintVmStatus(task.Task):
    def execute(self, vm_id, vm_status):
        print "VM %d - is %s" % (vm_id, vm_status)
