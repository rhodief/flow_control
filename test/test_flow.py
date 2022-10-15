from typing import Any, Callable, List
import unittest
from flow_control.execution_control import TicketManager, Transporter
from flow_control.interfaces import CallableExecutor
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, composite, SearchStrategy, text
from flow_control.flows import Flow, Sequence
import random
import inspect

from test.utils import random_transporter



class FunctionGenerator:
    def __init__(self, type: str, operation: str, val = int,iter = False) -> Any:
        self._callable_type = type
        self._operation_type = operation
        self._iter = iter
        self._val = val
    def _operation(self, a):
        ops = {
            '+': a + self._val,
            '-': a - self._val,
            '*': a * self._val,
            '/': a / self._val
        }
        return ops[self._operation_type]
    def _function_content(self, data):
        if iter:
            return [self._operation(d) for d in data]
        return self._operation(data)
    def generate(self):
        class ClsGen(CallableExecutor):
            def __init__(self, main_class: FunctionGenerator) -> None:
                self._main = main_class
            def __call__(self, data: Any, f) -> Any:
                return self._main._function_content(data)
        def fn_gen(data, f):
            return self._function_content(data)
        index = [ClsGen(self), fn_gen]
        if self._callable_type == 'random':
            i = random.randint(0,1)
            return index[i]
        if self._callable_type == 'class':
            return index[0]
        return index[1]
    
        

class TestSequence(unittest.TestCase):
    def test_sequence_class_instance(self):
        def fn_test(x):
            pass
        class TestCls(CallableExecutor):
            pass
        self.assertTrue(Sequence(executors=[lambda x: x + 1]), 'Fail on lambda function')
        self.assertTrue(Sequence((fn_test,)), 'Fail on function')
        self.assertTrue(Sequence([TestCls]), 'Fail on class')
    
    def test_shoud_fail_on_not_allowed_executors_types(self):
        with self.assertRaises(AssertionError):
            sequence = Sequence('a')
            sequence = Sequence(21)
            sequence = Sequence(('a', 1))

    @given(random_transporter())
    def test_sequence_call(self, transporter: Transporter):
        data = transporter._data
        fn1 = FunctionGenerator('random', '+', 4, True).generate()
        fn2 = FunctionGenerator('class', '*', 7, True).generate()
        fn3 = FunctionGenerator('fn', '-', 3, True).generate()
        sequence = Sequence(executors=[fn1, fn2, fn3])
        result = sequence(transporter)
        expected_result = [(d + 4) * 7 - 3 for d in data]
        self.assertEqual(result._data, expected_result)

    def test_analyze_method(self):
        fn1 = FunctionGenerator('class', '+', 4, True).generate()
        fn2 = FunctionGenerator('class', '*', 7, True).generate()
        fn3 = FunctionGenerator('fn', '-', 3, True).generate()
        sequence = Sequence(executors=[fn1, fn2, fn3])
        tm = TicketManager()
        node = sequence._analyze(tm)
        expected = {'name': 'Sequence', 'type': 'Sequence', 'index': '0', 'children': [{'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.0', 'children': []}, {'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.1', 'children': []}, {'name': 'fn_gen', 'type': 'function', 'index': '0.2', 'children': []}]}
        self.assertAlmostEqual(node, expected)
        

        
    

    


class TestFlow(unittest.TestCase):
    '''
    Test flow Class
    '''
    def setUp(self) -> None:
        pass
    @given(text())
    def test_flow_get_inicial_data(self, text):
        '''
        Test Correct passing of initial data
        '''
        flow = Flow(text)
        self.assertEqual(flow._inicial_data, text)
    def test_assertion_error_instanciation(self):
        with self.assertRaises(AssertionError):
            f = Flow(None, 'a', 'b', 'c')
    
    def test_analyze(self):
        pass
   
        

if __name__ == '__main__':
    unittest.main()



        

