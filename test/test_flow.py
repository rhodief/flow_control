from typing import Any, Callable, List
import unittest
from flow_control.execution_control import ControlStatus, TicketManager, Transporter, CallableExecutor
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, composite, SearchStrategy, text
from flow_control.flows import Flow, Map, Parallel, Sequence
import random


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
            '/': a / self._val if self._val != 0 else None
        }
        return ops[self._operation_type]
    def _function_content(self, data):
        if self._iter:
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
    
    def test_should_fail_on_not_allowed_executors_types(self):
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
        tm = TicketManager()
        sequence._analyze(tm)
        transporter._execution_control.controls._current._current_status.set_status(ControlStatus.RUNNING)
        result = sequence(transporter)
        expected_result = [(d + 4) * 7 - 3 for d in data]
        self.assertEqual(result._data, expected_result)

    def test_analyze_method(self):
        fn1 = FunctionGenerator('class', '+', 4, True).generate()
        fn2 = FunctionGenerator('class', '*', 7, True).generate()
        fn3 = FunctionGenerator('fn', '-', 3, True).generate()
        sequence = Sequence(executors=[fn1, fn2, fn3])
        tm = TicketManager()
        node = sequence._analyze(tm).to_dict()
        expected = {'name': 'Sequence', 'type': 'Sequence', 'index': '0', 'children': [{'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.0', 'children': []}, {'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.1', 'children': []}, {'name': 'fn_gen', 'type': 'function', 'index': '0.2', 'children': []}]}
        self.assertAlmostEqual(node, expected)


class TestMap(unittest.TestCase):
    def test_map_class_instance(self):
        def fn_test(x):
            pass
        class TestCls(CallableExecutor):
            pass
        self.assertTrue(Map(executors=[lambda x: x + 1]), 'Fail on lambda function')
        self.assertTrue(Map((fn_test,)), 'Fail on function')
        self.assertTrue(Map([TestCls]), 'Fail on class')
    
    def test_should_fail_on_not_allowed_executors_types(self):
        with self.assertRaises(AssertionError):
            sequence = Map('a')
            sequence = Map(21)
            sequence = Map(('a', 1))
    @given(random_transporter())
    def test_map_call(self, transporter: Transporter):
        data = transporter._data
        fn1 = FunctionGenerator('random', '+', 4).generate()
        fn2 = FunctionGenerator('class', '*', 7).generate()
        fn3 = FunctionGenerator('fn', '-', 3).generate()
        map_executor = Map(executors=[fn1, fn2, fn3])
        tm = TicketManager()
        map_executor._analyze(tm)
        transporter._execution_control.controls._current._current_status.set_status(ControlStatus.RUNNING)
        result = map_executor(transporter)
        expected_result = [(d + 4) * 7 - 3 for d in data]
        self.assertEqual(result._data, expected_result)

    def test_analyze_method(self):
        fn1 = FunctionGenerator('class', '+', 4, True).generate()
        fn2 = FunctionGenerator('class', '*', 7, True).generate()
        fn3 = FunctionGenerator('fn', '-', 3, True).generate()
        sequence = Map(executors=[fn1, fn2, fn3])
        tm = TicketManager()
        node = sequence._analyze(tm).to_dict()
        expected = {'name': 'Map', 'type': 'Map', 'index': '0', 'children': [{'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.0', 'children': []}, {'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.1', 'children': []}, {'name': 'fn_gen', 'type': 'function', 'index': '0.2', 'children': []}]}
        self.assertAlmostEqual(node, expected)

class TestParallel(unittest.TestCase):
    def test_parallel_class_should_fail_on_not_allowed_executors_types(self):
        with self.assertRaises(AssertionError):
            def fn_test(x):
                pass
            class TestCls(CallableExecutor):
                pass
            Parallel(flows=[lambda x: x + 1])
            Parallel(flows=(fn_test,))
            Parallel(flows=[TestCls])
    
    def test_parallel_analyze_method(self):
        f1 = Flow().sequence([lambda x: x + 1, lambda y: y-5]).map([lambda x: x *2])
        f2 = Flow().sequence([lambda x: x + 1]).map([lambda x: x *2, lambda y: y-5])
        tm = TicketManager()
        an = Parallel([f1, f2])._analyze(tm)
        expected_value = {'name': 'Parallel', 'type': 'Parallel', 'index': '0', 'children': [{'name': 'My Flow', 'type': 'Flow', 'index': '0.0', 'children': [{'name': 'Sequence', 'type': 'Sequence', 'index': '0.0.0', 'children': [{'name': '<lambda>', 'type': 'function', 'index': '0.0.0.0', 'children': []}, {'name': '<lambda>', 'type': 'function', 'index': '0.0.0.1', 'children': []}]}, {'name': 'Map', 'type': 'Map', 'index': '0.0.1', 'children': [{'name': '<lambda>', 'type': 'function', 'index': '0.0.1.0', 'children': []}]}]}, {'name': 'My Flow', 'type': 'Flow', 'index': '0.1', 'children': [{'name': 'Sequence', 'type': 'Sequence', 'index': '0.1.0', 'children': [{'name': '<lambda>', 'type': 'function', 'index': '0.1.0.0', 'children': []}]}, {'name': 'Map', 'type': 'Map', 'index': '0.1.1', 'children': [{'name': '<lambda>', 'type': 'function', 'index': '0.1.1.0', 'children': []}, {'name': '<lambda>', 'type': 'function', 'index': '0.1.1.1', 'children': []}]}]}]}
        self.assertEqual(an.to_dict(), expected_value)
    
    @given(lists(integers()), integers(), integers(), integers())
    def test_parallel_call_method(self, list_integers, int1, int2, int3):
        fn1 = FunctionGenerator('random', '+', int1, True).generate()
        fn2 = FunctionGenerator('class', '*', int2, True).generate()
        fn3 = FunctionGenerator('fn', '-', int3, True).generate()
        fn4 = FunctionGenerator('class', '*', int2).generate()
        fn5 = FunctionGenerator('fn', '+', int3).generate()
        fn6 = FunctionGenerator('random', '+', int1).generate()
        f1 = Flow() \
                .sequence([fn1]) \
                .map(execs=[fn4])
        f2 = Flow() \
                .sequence([fn2]) \
                .map(execs=[fn5]) 
        main_flow = Flow(list_integers) \
                .sequence([fn3]) \
                .map(execs=[fn6]) \
                .parallel([f1, f2])
        
        expected_value_main_flow = [(d - int3) + int1 for d in list_integers]
        expected_value_f1 = [(e + int1) * int2 for e in expected_value_main_flow]
        expected_value_f2 = [(e * int2) + int3 for e in expected_value_main_flow]
        total_expected = [expected_value_f1, expected_value_f2]
        self.assertEqual(main_flow.result(), total_expected)
    
    

    
                    
        
        
    

class TestFlow(unittest.TestCase):
    '''
    Test flow Class
    '''
    def setUp(self) -> None:
        pass
    @given(text())
    def test_flow_get_initial_data(self, text):
        '''
        Test Correct passing of initial data
        '''
        flow = Flow(text)
        self.assertEqual(flow._initial_data, text)
    def test_assertion_error_instanciation(self):
        with self.assertRaises(AssertionError):
            f = Flow(None, 'a', 'b', 'c')
    
    @given(lists(integers()))
    def test_flow_analyze_method(self, list_integers: List[int]):
        fn1 = FunctionGenerator('class', '+', 4, True).generate()
        fn2 = FunctionGenerator('class', '*', 7, True).generate()
        fn3 = FunctionGenerator('fn', '-', 3, True).generate()
        flow_analyze = Flow(list_integers) \
                .sequence(execs=[fn1, fn2, fn3]) \
                ._analyze()
        expected = {'name': 'My Flow', 'type': 'Flow', 'index': '0', 'children': [{'name': 'Sequence', 'type': 'Sequence', 'index': '0.0', 'children': [{'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.0.0', 'children': []}, {'name': 'ClsGen', 'type': 'ClsGen', 'index': '0.0.1', 'children': []}, {'name': 'fn_gen', 'type': 'function', 'index': '0.0.2', 'children': []}]}]}
        self.assertAlmostEqual(flow_analyze.to_dict(), expected)
        
    @given(lists(integers()), integers(), integers(), integers())
    def test_flow_result_method(self, list_integers: List[int], int1:int, int2:int, int3:int):
        fn1 = FunctionGenerator('random', '+', int1, True).generate()
        fn2 = FunctionGenerator('class', '*', int2, True).generate()
        fn3 = FunctionGenerator('fn', '-', int3, True).generate()
        fn4 = FunctionGenerator('class', '*', int2).generate()
        fn5 = FunctionGenerator('fn', '+', int3).generate()
        result = Flow(list_integers) \
                    .sequence([fn1, fn2, fn3]) \
                    .map(execs=[fn4, fn5]) \
                    .result()
        expected_result = [((i + int1) * int2 - int3) * int2 + int3 for i in list_integers]
        self.assertEqual(result, expected_result)

    
   
        

if __name__ == '__main__':
    unittest.main()



        

