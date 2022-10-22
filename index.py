
from typing import Any, List
from unittest import result
from flow_control.execution_control import CallableExecutor, FlowPanel
from flow_control.flows import Flow, Parallel
import time



def somar_cinco(nums: List[int], _e):
    return [n + 5 for n in nums]

class Multiplica(CallableExecutor):
    def __init__(self, valor: int, iterable = False) -> None:
        self._valor = valor
        self._iterable = iterable
    def __call__(self, data: Any, flow_panel: FlowPanel) -> Any:
        time.sleep(4)
        if self._iterable:
            return data * self._valor
        return [d * self._valor for d in data]
    
flow = Flow([0,1,2,3,4,5]) \
            .sequence([somar_cinco, Multiplica(2)]) \
            .map([Multiplica(2, True), Multiplica(3, True), Multiplica(5, True)]) \
            .parallel([
                Flow().sequence([somar_cinco, Multiplica(2)]),
                Flow().map([Multiplica(2, True), Multiplica(3, True), Multiplica(5, True)])
            ]) \
            .sequence([lambda x, y: x, lambda x, y: x])
            
r = flow.result()
print(r)
    