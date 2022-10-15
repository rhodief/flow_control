
from typing import Any
from abc import ABC

class IFlowControl(ABC):
    def data_store(self):
        ''''''
    def execution_control(self):
        ''''''
    def logger(self):
        ''''''

class CallableExecutor():
    def __call__(self, data: Any, flow_control: IFlowControl) -> Any:
        '''
        '''
        raise NotImplementedError('Please, implement method .__call__()')


