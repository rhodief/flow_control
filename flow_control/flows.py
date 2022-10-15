from queue import Queue
from types import FunctionType
from typing import Any, Iterable, Tuple, Union
from typing_extensions import Self
from flow_control.controls import DataStore
from flow_control.execution_control import Articulator, Ticket, TicketManager, Transporter, TreeNode, ExecutionControl
from flow_control.interfaces import CallableExecutor
from flow_control.output import SuperLogger


class Sequence(Articulator):
    def __init__(
        self, executors: Tuple[Union[CallableExecutor, FunctionType]],
        name = '') -> None:
        assert isinstance(executors, Iterable), 'executors param must be a iterable'
        assert all([hasattr(el, '__call__') or isinstance(el, FunctionType) for el in executors]), 'Executors must be a CallableExecutor subclass or FunctionType'
        self._callable_executors = executors
        self._name = name
        self._node: TreeNode = None
    def __call__(self, transporter: Transporter) -> Any:
        for call_exec in self._callable_executors:
            transporter.receive_data(call_exec(*transporter.deliver())) 
        return transporter
    def _analyze(self, tm: TicketManager):
        self._node = self._set_nodes(self._callable_executors, tm)
        return self._node.to_dict()
        
class Map(Articulator):
    pass

class Parallel(Articulator):
    pass
    
class ExecutionQueue(Articulator):
    def __init__(self) -> None:
        self._queue = []
    def push(self):
        '''
        Add a task to the queue
        '''
    def analyze(self, ticket_manager: TicketManager):
        '''
        Check the execution tree and retrieve the execution Tree
        '''
    def __call__(self, transporter: Transporter) -> Any:
        '''
        Start the execution queue
        '''

class Flow(Articulator):
    def __init__(self, initial_data: Any = None, data_store: DataStore = None, super_logger: SuperLogger = None, queue: Queue = False) -> None:
        if data_store:
            assert isinstance(data_store, DataStore), 'data_store must be a DataStore() instance'
        if super_logger:
            assert isinstance(super_logger, SuperLogger), 'super_logger must be a SuperLogger instance'
        if queue:
            assert isinstance(queue, Queue), 'queue must be a Queue() instance'
        self._inicial_data = initial_data
        self._data_store = data_store if data_store else DataStore()
        self._super_logger = super_logger
        self._q = queue
        if not self._q:
            self._q = Queue()
        if not self._super_logger:
            self._super_logger = SuperLogger(self._q)
        self._execution_control = ExecutionControl(self._q)
        self._execution_queue = []
        self._transporter = Transporter()
    def sequence(self, exec = Iterable[CallableExecutor]) -> Self:
        '''
        It runs a List of Callable to be executed in sequence.
        '''
        return self
    def map(self, exec = Iterable[CallableExecutor]) -> Self:
        '''
        It runs in parallel for each element of the iterable to pass through the sequence of callables
        '''
        return self
    def reduce(self) -> Self:
        return self
    def merge(self) -> Self:
        return self
    def parallel(self, exec = Iterable[Self]) -> Self:
        return self
    def break_point(self) -> Self:
        return self
    def join_flow(self, flow:Iterable[Self]) -> Self:
        return self
    def result(self) -> Any:
        return 'Resultado'
    def analyze(self, ticket: Ticket):
        pass
    def __call__(self, transporter: Transporter) -> Any:
        pass
    