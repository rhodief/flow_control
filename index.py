
from typing import Any, List
from unittest import result
from flow_control.execution_control import CallableExecutor, FlowPanel
from flow_control.flows import Flow




def somar_cinco(nums: List[int], _e):
    return [n + 5 for n in nums]

class Multiplica(CallableExecutor):
    def __init__(self, valor: int) -> None:
        self._valor = valor
    def __call__(self, data: Any, flow_panel: FlowPanel) -> Any:
        return [self._valor * d for d in data]
    
flow = Flow([0,1,2,3,4,5]) \
            .sequence([somar_cinco, Multiplica(2)])
            
print(flow.result())
    