from taskflow import task
from taskflow.patterns import linear_flow
from taskflow import engines


class Task1(task.Task):
    def execute(self):
        return "new value"


class Task2(task.Task):
    old_param = "old value"

    def execute(self, param2):
        prev_value = self.old_param
        self.old_param = param2

        print self.old_param
        return (param2, prev_value)

    def revert(self, **kwargs):
        print "Task2%s" % kwargs


class BadTask(task.Task):
    def execute(self):
        raise IOError("Broken")

    def revert(self, **kwargs):
        print "BadTask%s" % kwargs


flow = linear_flow.Flow('flow name').add(
    Task1(provides='param2'),
    Task2(),
    BadTask(),
)

try:
    engines.run(flow)
except Exception as e:
    pass
