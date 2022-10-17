from queue import Queue
from types import FunctionType
from typing import Any, Iterable, List, Tuple, Union
from typing_extensions import Self
from flow_control.controls import DataStore
from flow_control.execution_control import Articulator, ControlStatus, FlowBroker, Ticket, TicketManager, Transporter, TreeNode, ExecutionControl, CallableExecutor
from flow_control.output import PrinterWorker, SuperPrinter
from flow_control.threads_control import FlowThreads


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
        controls = transporter._execution_control.controls
        for index, call_exec in enumerate(self._callable_executors):
            if controls.can_I_execute():
                current_child: TreeNode = self._node.children[index]
                controls.exec_start(self._node, current_child)
                transporter.receive_data(call_exec(*transporter.deliver()))
                controls.exec_finish(current_child.ticket.tid)
        return transporter
    def _analyze(self, tm: TicketManager):
        self._node = self._set_nodes(self._callable_executors, tm)
        return self._node
        
class Map(Articulator):
    def __init__(self, executors = Tuple[Union[CallableExecutor, FunctionType]], max_workers = 10, name = '') -> None:
        assert isinstance(executors, Iterable), 'executors param must be a iterable'
        assert all([hasattr(el, '__call__') or isinstance(el, FunctionType) for el in executors]), 'Executors must be a CallableExecutor subclass or FunctionType'
        self._callable_executors = executors
        self._node: TreeNode = None
        self._name = name
        self._max_workers = max_workers
    def __call__(self, transporter: Transporter) -> Any:
        transporter_clones = transporter.clone_for_iterable()
        def parallel_task(task_transporter: Transporter, task_executors: List[Articulator]):
            controls = task_transporter._execution_control.controls
            if controls.can_I_execute():
                for index, call_exec in enumerate(task_executors):
                    current_child: TreeNode = self._node.children[index]
                    controls.exec_start(self._node, current_child, task_transporter._n_iter, task_transporter._n_total)
                    task_transporter.receive_data(call_exec(*task_transporter.deliver()))
                    controls.exec_finish(current_child.ticket.tid)
            return task_transporter
        result_transporter = FlowThreads(parallel_task, transporter_clones, self._callable_executors, n_workers=self._max_workers).run()
        transporter.recompose(result_transporter)
        return transporter
    def _analyze(self, tm: TicketManager):
        self._node = self._set_nodes(self._callable_executors, tm)
        return self._node


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
    def map(self, execs = Iterable[CallableExecutor]) -> Self:
        '''
        It runs in parallel for each element of the iterable to pass through the sequence of callables
        '''
        self._execution_queue.append(Map(execs))
        return self
    def reduce(self) -> Self:
        return self
    def merge(self) -> Self:
        return self
    def parallel(self, flows = Iterable[Self]) -> Self:
        self._execution_queue.append(Parallel(flows=flows))
        return self
    def break_point(self) -> Self:
        return self
    def join_flow(self, flow:Iterable[Self]) -> Self:
        return self
    def result(self) -> Any:
        self._broker.put(self._analyze().to_dict())
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
        self._transporter = transporter
        self._data_store = transporter._data_store
        self._execution_control = transporter._execution_control
        self._run()
        return self._transporter
    def _set_flow_status(self, status: ControlStatus):
        self._execution_control.controls._current._current_status.set_status(status)
    def _run(self):
        transporter = self._transporter
        for executor in self._execution_queue:
             transporter = executor(transporter)
        self._transporter = transporter

class Parallel(Articulator):
    def __init__(self, flows: Iterable[Flow], name = '', max_workers = 10) -> None:
        assert isinstance(flows, Iterable), 'flows param must be a iterable'
        assert all([isinstance(f, Flow) for f in flows]), 'Executors must be a CallableExecutor subclass or FunctionType'
        self._flows = flows
        self._name = name
        self._max_workers = max_workers
        self._node: TreeNode = None
    def _analyze(self, tm: TicketManager):
        self._node = self._set_nodes(self._flows, tm)
        return self._node
    def __call__(self, transporter: Transporter) -> Any:
        print('estou aqui')
        clones = transporter.clone(len(self._flows))
        branches = zip(self._flows, clones)
        def parallel_task(_branches: Tuple[Flow, Transporter], _):
            _flow, _transporter = _branches
            print(_flow, _transporter)
            return _flow(_transporter)
        result_transporter = FlowThreads(parallel_task, branches, n_workers=self._max_workers).run()
        transporter.recompose(result_transporter)
        return transporter


    
    