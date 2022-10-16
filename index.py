
from typing import List
from flow_control.execution_control import CallableExecutor




def somar_cinco(nums: List[int]):
    return [n + 5 for n in nums]

class Multiplica(CallableExecutor):
    def __init__(self, valor: int) -> None:
        self._valor = valor
    
    