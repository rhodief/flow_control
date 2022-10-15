
from flow_control.execution_control import ExecutionFamily, ExecutionNode, Ticket, Transporter
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, composite, SearchStrategy
from typing import Any, Callable, List

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

@composite
def random_transporter(draw: Callable[[SearchStrategy[Any]], List[Any]]):
    list_integer = draw(lists(integers(), min_size = 0, max_size = 10))
    transporter = Transporter(list_integer)
    return transporter

