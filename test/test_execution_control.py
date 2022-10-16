from datetime import datetime
import unittest
from flow_control.execution_control import ControlStatus, Controls, CurrentExecution, ExecutionControl, ExecutionEvents, ExecutionFamily, ExecutionNode, FlowPanel, Status, Ticket, TicketManager, Transporter, TreeNode
from hypothesis import given, assume
from hypothesis.strategies import integers, lists

from test.utils import broker_instance, random_transporter


class TestTicket(unittest.TestCase):
    @given(lists(integers(min_value = 0, max_value = 5)), integers())
    def test_index_list_must_can_not_be_empty(self, list_integers, ints):
        with self.assertRaises(AssertionError):
            ticket = Ticket([])
    
    @given(lists(integers(min_value = 0, max_value = 5)))
    def test_tid(self, list_integers):
        assume(list_integers != [])
        ticket = Ticket(list_integers)
        expected_tid = ticket._MAIN_SEPARATOR.join([str(i) for i in list_integers])
        self.assertEqual(ticket.tid, expected_tid)
    
    @given(lists(integers(min_value = 0, max_value = 5)), integers())
    def test_index_must_be_integers(self, list_integers, ints):
        assume(list_integers != [])
        list_text = [str(i) for i in list_integers]
        with self.assertRaises(AssertionError):
            ticket = Ticket(list_text)
        with self.assertRaises(AssertionError):
            ticket = Ticket(ints)
    @given(lists(integers(min_value = 0, max_value = 10)), integers(min_value = 0), integers(min_value = 0))
    def test_set_iter(self, list_integers, n_iter, n_total):
        assume(list_integers != [])
        assume(n_iter > -1)
        assume(n_total > -1)
        ticket = Ticket(list_integers)
        ticket.set_iter(n_iter, n_total)
        expected_main_value = ticket._MAIN_SEPARATOR.join([str(i) for i in list_integers])
        expected_iter_value = f'{ticket._ITER_SEPARATOR}{n_iter}'
        self.assertEqual(ticket.tid, expected_main_value + expected_iter_value)
        self.assertEqual(ticket.total, n_total)


class TestTicketManager(unittest.TestCase):
    @given(integers(min_value = 1, max_value = 5))
    def test_next_method(self, steps):
        ticket_manager = TicketManager()
        ticket: Ticket
        for s in range(steps):
            ticket = ticket_manager.next()
        expected_value = steps - 1
        self.assertEqual(ticket.tid, str(expected_value))

    @given(integers(min_value = 1, max_value = 2), integers(min_value = 1, max_value = 5))
    def test_child_step(self, main_step, child_step):
        ticket_manager = TicketManager()
        ticket: Ticket
        for s in range(main_step):
            ticket = ticket_manager.next()
        ticket_manager.open_child_depth()
        for s in range(child_step):
            ticket = ticket_manager.next()
        expected_value = f'{main_step -1}.{child_step -1}'
        self.assertEqual(ticket.tid, str(expected_value))
        ticket_manager.close_child_depth()
        ticket_manager.next()
        expected_value = f'{main_step}'

    @given(integers(min_value = 1, max_value = 2), integers(min_value = 1, max_value = 5))
    def test_child_step(self, main_step, child_step):
        ticket_manager = TicketManager()
        ticket: Ticket
        for s in range(main_step):
            ticket = ticket_manager.next()
        ticket_manager.open_child_depth()
        for s in range(child_step):
            ticket = ticket_manager.next()
        expected_value = f'{main_step -1}.{child_step -1}'
        self.assertEqual(ticket.tid, str(expected_value))
        ticket_manager.close_child_depth()
        ticket_manager.next()
        expected_value = f'{main_step}'

    def test_cant_open_or_close_depth_with_no_prev_next(self):
        ticket_manager = TicketManager()
        with self.assertRaises(AssertionError):
            ticket_manager.open_child_depth()
        with self.assertRaises(AssertionError):
            ticket_manager.close_child_depth()

class TestExecutionEvents(unittest.TestCase):
    def test_check_queue_instance(self):
        b = broker_instance()
        ev = ExecutionEvents(b)
        self.assertTrue(ev)
    def test_should_fail_on_parameter_other_than_queue(self):
        with self.assertRaises(AssertionError):
            ev = ExecutionEvents('')
            self.assertTrue(ev)
    
    def test_start_emmition(self):
        b = broker_instance()
        ev = ExecutionEvents(b)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        en1 = ExecutionNode(TreeNode('parent', 'Sequence', t1))
        en2 = ExecutionNode(TreeNode('child', 'Function', t2))
        ef = ExecutionFamily(en1, en2)
        ev.emmit_start(ef)
        result = b.get()
        self.assertEqual(result['type'], 'start')
        self.assertTrue(isinstance(result['parent'], dict))

    def test_finish_emmition(self):
        b = broker_instance()
        ev = ExecutionEvents(b)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        en1 = ExecutionNode(TreeNode('parent', 'Sequence', t1))
        en2 = ExecutionNode(TreeNode('child', 'Function', t2))
        ef = ExecutionFamily(en1, en2)
        ev.emmit_finish(ef)
        result = b.get()
        self.assertEqual(result['type'], 'finish')
        self.assertTrue(isinstance(result['parent'], dict))


class TestCurrentExecution(unittest.TestCase):
    def test_current_execution_instance(self):
        b = broker_instance()
        current_execution = CurrentExecution(Status(), ExecutionEvents(b))
        self.assertTrue(current_execution)
    def test_current_execution_should_fail_check_deps(self):
        with self.assertRaises(AssertionError):
            current_execution = CurrentExecution('', '')
            self.assertTrue(current_execution)
    def test_add_method_index(self):
        b = broker_instance()
        ev = ExecutionEvents(b)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        en1 = ExecutionNode(TreeNode('parent', 'Sequence', t1))
        en2 = ExecutionNode(TreeNode('child', 'Function', t2))
        ef = ExecutionFamily(en1, en2)
        current_execution = CurrentExecution(Status(), ev)
        current_execution.add(ef)
        result = current_execution._current_execution.get(ef.get_tid())
        self.assertTrue(result)
    def test_add_method_emmition(self):
        b = broker_instance()
        ev = ExecutionEvents(b)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        en1 = ExecutionNode(TreeNode('parent', 'Sequence', t1))
        en2 = ExecutionNode(TreeNode('child', 'Function', t2))
        ef = ExecutionFamily(en1, en2)
        current_execution = CurrentExecution(Status(), ev)
        current_execution.add(ef)
        result = b.get()
        self.assertEqual(result['type'], 'start')
        self.assertTrue(isinstance(result['current'], dict))
    
    def test_remove_method_index(self):
        q = broker_instance()
        ev = ExecutionEvents(q)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        en1 = ExecutionNode(TreeNode('parent', 'Sequence', t1))
        en2 = ExecutionNode(TreeNode('child', 'Function', t2))
        ef = ExecutionFamily(en1, en2)
        current_execution = CurrentExecution(Status(), ev)
        current_execution.add(ef)
        current_execution.remove('0.0')
        result = current_execution._current_execution.get(ef.get_tid())
        self.assertIsNone(result)
    def test_remove_method_emmition(self):
        q = broker_instance()
        ev = ExecutionEvents(q)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        en1 = ExecutionNode(TreeNode('parent', 'Sequence', t1))
        en2 = ExecutionNode(TreeNode('child', 'Function', t2))
        ef = ExecutionFamily(en1, en2)
        current_execution = CurrentExecution(Status(), ev)
        current_execution.add(ef)
        current_execution.remove('0.0')
        result = q.get()
        result = q.get()
        self.assertEqual(result['type'], 'finish')
        self.assertTrue(isinstance(result['current'], dict))



class TestControl(unittest.TestCase):
    def setUp(self) -> None:
        q = broker_instance()
        ev = ExecutionEvents(q)
        self.currentExecution = (CurrentExecution(Status(), ev), q)
    def test_exec_can_i_execute(self):
        execution, q = self.currentExecution
        controls = Controls(execution)
        self.assertFalse(controls.can_I_execute())
    def test_exec_not_running_action_should_do_nothing(self):
        execution, q = self.currentExecution
        controls = Controls(execution)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        t1 = TreeNode('parent', 'Sequence', t1)
        t2 = TreeNode('child', 'Function', t2)
        controls.exec_start(t1, t2)
        self.assertTrue(not any(controls._current._current_execution))
    def test_exec_start_assign_datetime(self):
        execution, q = self.currentExecution
        controls = Controls(execution)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        t1 = TreeNode('parent', 'Sequence', t1)
        t2 = TreeNode('child', 'Function', t2)
        controls._current._current_status.set_status(ControlStatus.RUNNING)
        controls.exec_start(t1, t2)
        self.assertTrue(isinstance(controls._current.get_by_tid('0.0').get_current()._start, datetime))
    def test_exec_finish_empty_execution(self):
        execution, q = self.currentExecution
        controls = Controls(execution)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        t1 = TreeNode('parent', 'Sequence', t1)
        t2 = TreeNode('child', 'Function', t2)
        controls._current._current_status.set_status(ControlStatus.RUNNING)
        controls.exec_start(t1, t2)
        controls.exec_finish(t2.ticket.tid)
        self.assertTrue(not any(controls._current._current_execution))
    def test_exec_finish_time_execution(self):
        execution, q = self.currentExecution
        controls = Controls(execution)
        tm = TicketManager()
        t1 = tm.next()
        tm.open_child_depth()
        t2 = tm.next()
        t1 = TreeNode('parent', 'Sequence', t1)
        t2 = TreeNode('child', 'Function', t2)
        controls._current._current_status.set_status(ControlStatus.RUNNING)
        controls.exec_start(t1, t2)
        controls.exec_finish(t2.ticket.tid)
        ev = q.get()
        ev = q.get()
        ev_type = ev['type']
        ec_fam = ev['current']
        self.assertEqual(ev_type, 'finish')
        self.assertTrue(isinstance(ec_fam['end'], datetime))
        
class TestExecutionControl:
    pass
        
class TestTransporter(unittest.TestCase):
    @given(random_transporter())
    def test_deliver_method(self, transporter: Transporter):
        value = transporter._data
        deliver = transporter.deliver()
        data, flow_panel = deliver
        self.assertEqual(data, value)
        self.assertTrue(isinstance(flow_panel, FlowPanel))
    @given(random_transporter(), integers())
    def test_deliber_receive_data(self, transporter: Transporter, data: int):
        transporter.receive_data(data)
        self.assertEqual(transporter._data, data)

if __name__ == '__main__':
    unittest.main()




