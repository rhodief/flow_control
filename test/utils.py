
from queue import Queue
from flow_control.controls import DataStore
from flow_control.execution_control import ExecutionControl, ExecutionFamily, ExecutionNode, FlowBroker, Ticket, Transporter
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, composite, SearchStrategy
from typing import Any, Callable, List

from flow_control.output import Broker

@composite
def random_ticket(draw: Callable[[SearchStrategy[Any]], List[Any]], iter = False):
    list_integer = draw(lists(integers(0, 10)))
    n_iter = draw(integers())
    n_total = draw(integers())
    assume(list_integer != [])
    ticket = Ticket(list_integer)
    if iter:
        ticket.set_iter(n_iter, n_total)
    return ticket

def broker_instance():
    return FlowBroker(Queue())
    

@composite
def random_transporter(draw: Callable[[SearchStrategy[Any]], List[Any]]):
    list_integer = draw(lists(integers(), min_size = 0, max_size = 10))
    execution_control = ExecutionControl(broker_instance())
    data_store = DataStore()
    return Transporter(execution_control, data_store, list_integer)
    

