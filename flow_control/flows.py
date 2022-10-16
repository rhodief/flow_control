from queue import Queue
from types import FunctionType
from typing import Any, Iterable, Tuple, Union
from typing_extensions import Self
from flow_control.controls import DataStore
from flow_control.execution_control import Articulator, ControlStatus, FlowBroker, Ticket, TicketManager, Transporter, TreeNode, ExecutionControl, CallableExecutor
from flow_control.output import PrinterWorker, SuperPrinter


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
        return self._node
        
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
    def _analyze(self, ticket_manager: TicketManager):
        '''
        Check the execution tree and retrieve the execution Tree
        '''
    def __call__(self, transporter: Transporter) -> Any:
        '''
        Start the execution queue
        '''

class Flow(Articulator):
    def __init__(self, initial_data: Any = None, data_store: DataStore = None, super_printer: SuperPrinter = None, broker: FlowBroker = None) -> None:
        if data_store:
            assert isinstance(data_store, DataStore), 'data_store must be a DataStore() instance'
        if super_printer:
            assert isinstance(super_printer, SuperPrinter), 'super_printer must be a SuperPrinter instance'
        if broker:
            assert isinstance(broker, FlowBroker), 'broker must be a FlowBroker() instance'
        self._initial_data = initial_data
        self._data_store = data_store if data_store else DataStore()
        self._super_printer = super_printer
        self._broker = broker
        if not self._broker:
            self._broker = FlowBroker(Queue())
        if not self._super_printer:
            printer_worker = PrinterWorker()
            self._super_printer = SuperPrinter(self._broker, printer_worker)
        self._execution_control = ExecutionControl(self._broker)
        self._transporter = Transporter(self._execution_control, self._data_store, self._initial_data)
        self._ticket_manager = TicketManager()
        self._execution_queue = []
        self._name = 'My Flow'
        
    def sequence(self, execs = Iterable[CallableExecutor]) -> Self:
        '''
        It runs a List of Callable to be executed in sequence.
        '''
        self._execution_queue.append(Sequence(execs))
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
        #self._broker.put(self._analyze())
        self._set_flow_status(ControlStatus.RUNNING)
        self._super_printer.watch()
        self._run()
        self._super_printer.block()
        self._set_flow_status(ControlStatus.IDLE)
        return self._transporter._data
    def _analyze(self, ticket_manager: TicketManager = None):
        tm = ticket_manager if ticket_manager else self._ticket_manager
        self._node = self._set_nodes(self._execution_queue, tm)
        return self._node
    def __call__(self, transporter: Transporter) -> Any:
        pass
    def _set_flow_status(self, status: ControlStatus):
        self._execution_control.controls._current._current_status.set_status(status)
    def _run(self):
        transporter = self._transporter
        for executor in self._execution_queue:
             transporter = executor(transporter)
        self._transporter = transporter