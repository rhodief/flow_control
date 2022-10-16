from datetime import datetime
from enum import Enum
from types import FunctionType
from typing import Any, Callable, Dict, List, Tuple, Union
from typing_extensions import Self
from flow_control.controls import DataStore
from flow_control.output import Broker


class Ticket:
    def __init__(self, indexes: List[int]) -> None:
        assert isinstance(indexes, list), 'Invalid index value'
        assert len(indexes) > 0
        assert all(isinstance(i, int) for i in indexes)
        self._indexes = indexes
        self._iter:int = -1
        self._total:int = -1
        self._MAIN_SEPARATOR = '.'
        self._ITER_SEPARATOR = '-'
    @property
    def tid(self) -> str:
        '''
        TID is the string-form of the ticket
        '''
        main = self._MAIN_SEPARATOR.join([str(i) for i in self._indexes])
        if self._iter > -1:
            main+= f'{self._ITER_SEPARATOR}{self._iter}'
        return main
        
    def set_iter(self, n_iter:int, total:int):
        '''
        Set iter Index
        '''
        self._iter = n_iter
        self._total = total
    @property
    def n_iter(self):
        return self.n_iter
    @property
    def total(self):
        return self._total

class TicketManager:
    def __init__(self) -> None:
        self._depth = [-1]
    def next(self):
        '''
        Increase the main counter and release a ticket
        '''
        self._depth[-1] +=1
        return Ticket([*self._depth])

    def open_child_depth(self):
        '''
        Make child_counter to be increaseble
        '''
        assert self._depth[-1] > -1, 'Cannot open child depth with no previous "next" step'
        self._depth.append(-1)

    def close_child_depth(self):
        assert len(self._depth) > 1, 'Cannot close child one-level deep'
        del self._depth[-1]

class TreeNode:
    def __init__(self, name, type, ticket, children = []) -> None:
        self._name: str = name
        self._type: str = type
        self._ticket: Ticket = ticket
        self._children: List = children
    @property
    def name(self):
        return self._name
    @property
    def type(self):
        return self._type
    @property
    def ticket(self):
        return self._ticket
    @property
    def children(self):
        return self._children
    
    def to_dict(self):
        return {
            'name': self._name,
            'type': self._type,
            'index': self._ticket.tid,
            'children': [c.to_dict() for c in self._children]
        }

class ExecutionNode:
    def __init__(self, treeNode: TreeNode, n_iter = None, n_total = None) -> None:
        self._name = treeNode.name
        self._type = treeNode.type
        self._start: datetime = None
        self._end: datetime = None
        self._n_iter: int = n_iter
        self._total_iter: int = n_total
        self._ticket = treeNode.ticket
        self._ITER_SEPARATOR = '-'
    def set_start(self):
        self._start = datetime.now()
    def set_end(self):
        self._end = datetime.now()
    def get_tid(self):
        if self._n_iter: return f'{self._ticket.tid}{self._ITER_SEPARATOR}{self._n_iter}'
        return self._ticket.tid
    
    def to_dict(self):
        return {
            'name': self._name,
            'type': self._type,
            'index': self._ticket.tid,
            'start': self._start,
            'end': self._end,
            'n_iter': self._n_iter,
            'total_iter': self._total_iter
        }



    

class ControlStatus(Enum):
    IDLE = 'IDLE'
    RUNNING = 'RUNNING'
    ERROR = 'ERROR'
    STOPED = 'STOPED'

class Status:
    def __init__(self) -> None:
        self._status = ControlStatus.IDLE
    def set_status(self, status: ControlStatus):
        self._status = status
    def get_status(self) -> ControlStatus:
        return self._status

class ExecutionFamily:
    def __init__(self, parent_node: ExecutionNode, current_node: ExecutionNode) -> None:
        self._parent_node = parent_node
        self._current_node = current_node
        self._ticket = current_node._ticket
    def get_family(self):
        return [self._parent_node, self._current_node]
    def get_tid(self):
        return self._current_node.get_tid()
    def get_parent(self) -> ExecutionNode:
        return self._parent_node
    def get_current(self) -> ExecutionNode:
        return self._current_node
    

class FlowEvent:
    def __init__(self, flow_type: str, execution_family: ExecutionFamily, msgs: List[str] = []) -> None:
        self._type = flow_type
        self._execution_family = execution_family
        self._msgs = msgs
    @property
    def type(self):
        return self._type
    @property
    def execution_family(self):
        return self._execution_family
    @property
    def msgs(self):
        return self._msgs
    def to_dict(self):
        return {
            'type': self.type,
            'parent': self._execution_family.get_parent().to_dict(),
            'current': self._execution_family.get_current().to_dict()
        }

class FlowBroker(Broker):
    def get(self) -> FlowEvent:
        return super().get()



class ExecutionEvents:
    def __init__(self, broker: FlowBroker) -> None:
        assert isinstance(broker, FlowBroker), 'broker is not a FlowBroker instance'
        self._broker = broker
        self._on_event_emmit_callback = None
        self._on_start_emmit_callback = None
        self._on_finish_emmit_callback = None
        self._on_user_loggin_emmit_callback = None
    def emmit_start(self, execution_family: ExecutionFamily):
        self._global_emmitter('start', execution_family)
    def emmit_finish(self, execution_family:ExecutionFamily):
        self._global_emmitter('finish', execution_family)
    def _global_emmitter(self, ev_type:str, execution_family: ExecutionFamily):
        flow_event = FlowEvent(ev_type, execution_family).to_dict()
        self._broker.put(flow_event)
    def user_loggin(self, msgs: List[str] = []):
        pass
    def on_event_emmit(self, fn: Callable = None):
        pass
    def on_start_emmit(self, fn: Callable = None):
        pass
    def on_finish_emmit(self, fn: Callable = None):
        pass
    def on_user_loggin_emmit(self, fn: Callable = None):
        pass


class CurrentExecution:
    def __init__(self, status: Status, events: ExecutionEvents) -> None:
        assert isinstance(status, Status), 'status should be Status instance'
        assert isinstance(events, ExecutionEvents), 'execution events should be ExecutionEvents instance'
        self._current_status = status
        self._events = events
        self._current_execution: Dict[str, ExecutionFamily] = {}
    def add(self, execution_family: ExecutionFamily):
        self._current_execution[execution_family.get_tid()] = execution_family
        self._events.emmit_start(execution_family)
    def remove(self, tid: str):
        if self._current_execution[tid]:
            exection = self._current_execution[tid]
            exection.get_current().set_end()
            self._events.emmit_finish(exection)
            del self._current_execution[tid]
    def can_i_execute(self):
        status = self._current_status.get_status()
        return status == status.RUNNING
    def get_by_tid(self, tid:str)  -> ExecutionFamily:
        return self._current_execution.get(tid)
    
class Controls:
    def __init__(self, current: CurrentExecution) -> None:
        self._current = current
    def exec_start(self, parent_node: TreeNode, current_node: TreeNode, n_iter = None, total = None):
        if not self.can_I_execute(): return
        parent_execution_node = ExecutionNode(parent_node)
        current_execution_node = ExecutionNode(current_node)
        current_execution_node.set_start()
        self._current.add(ExecutionFamily(parent_execution_node, current_execution_node))
        return True
    def exec_finish(self, tid: str):
        if not self.can_I_execute(): return
        self._current.remove(tid)
    def can_I_execute(self) -> bool:
        '''
        Check the execution status
        '''
        return self._current.can_i_execute()
   
class UserLogger:
    def __init__(self, execution_events: ExecutionEvents) -> None:
        self._user_logger = execution_events.user_loggin
    def log(self, msg: str) -> None:
        self._user_logger([msg])
        
class FlowPanel:
    def __init__(self, user_logger: UserLogger, data_store: DataStore) -> None:
        self._user_logger = user_logger
        self._data_store = data_store
    def loger(self):
        return self._user_logger
    def data_store(self):
        return self.data_store

class ExecutionControl:
    def __init__(self, broker: FlowBroker) -> None:
        self._status = Status()
        self._events = ExecutionEvents(broker)
        self._current_execution = CurrentExecution(self._status, self._events)
        self._controls = Controls(self._current_execution)
    @property
    def controls(self) -> Controls:
        '''
        Expose the interaction with the flow
        '''
        return self._controls
        
    def status(self)-> ControlStatus:
        '''
        Show the status of the flow
        '''
        return self._status.get_status()
    def current_execution(self) -> CurrentExecution:
        '''
        Show the current execution
        '''
        return self._current_execution
    def events(self) -> ExecutionEvents:
        '''
        Execution Events
        '''
        return self._events
    def expose_user_logger(self) -> UserLogger:
        return UserLogger(self._current_execution._events)


class Transporter:
    def __init__(self, execution_control: ExecutionControl, data_store: DataStore, data: Any) -> None:
        self._data = data
        self._execution_control = execution_control
        self._data_store = data_store
    def deliver(self) -> Tuple[Any, FlowPanel]:
        flow_panel = FlowPanel(self._execution_control.expose_user_logger(), self._data_store)
        return self._data, flow_panel
    def receive_data(self, data):
        self._data = data
    def clone(self):
        pass
    def clone_for_iterable(self):
        pass

class CallableExecutor():
    def __call__(self, data: Any, flow_panel: FlowPanel) -> Any:
        '''
        '''
        raise NotImplementedError('Please, implement method .__call__()')

class Articulator():
    def __call__(self, transporter: Transporter) -> Any:
        '''
        Receive transporter for execution
        '''
        raise NotImplementedError('Please, implement method .__call__()')
    def _analyze(self, tm: TicketManager):
        '''
        Return a ExecutionTreeNode
        '''
        raise NotImplementedError('Please, implement method .__analyze()')
    
    def _get_executors(self, ticket: Ticket) -> Tuple[Ticket, Any]:
        '''
        Return list of Callable Executor or Flow. Use it to get the executors. 
        '''
        raise NotImplementedError('Please, implement method .__get_executors()')
    @property
    def name(self):
        return self._name if self._name else type(self).__name__
    @property
    def type(self):
        return type(self).__name__
    def _proper_name(self, obj: Union[CallableExecutor, FunctionType]) -> str:
        if hasattr(obj, 'name'): return obj.name
        if hasattr(obj, '__name__'): return obj.__name__
        return type(obj).__name__
    def _set_nodes(self, execs: Callable, tm: Ticket):
        current_ticket = tm.next()
        tm.open_child_depth()
        def proper_node(e):
            if hasattr(e, '_analyze'):
                return e._analyze(tm)
            return TreeNode(
                self._proper_name(e), 
                type(e).__name__,
                tm.next()
            )
        children_nodes = [proper_node(e) for e in execs]
        tm.close_child_depth()
        return TreeNode(
            self.name,
            self.type,
            current_ticket,
            children=children_nodes
        )

