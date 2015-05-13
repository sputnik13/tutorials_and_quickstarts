from taskflow.patterns import linear_flow
from taskflow import retry

import task


def create_cluster():
    flow = linear_flow.Flow('creating vm').add(
        task.CreateVm(),
        linear_flow.Flow('check vm status',
                         retry=retry.Times(attempts=5)
                         ).add(task.CheckVmStatus(provides='vm_status')),
        task.PrintVmStatus(),
    )
    return flow
