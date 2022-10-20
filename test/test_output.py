import unittest
from flow_control.output import FlowDesign
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, composite, SearchStrategy, text
import datetime

class TestSuperPrinterWorker(unittest.TestCase):
    def test_terminal_dict(self):
        messages = [
            {'name': 'My Flow', 'type': 'Flow', 'index': '0', 'children': [{'name': 'Sequence', 'type': 'Sequence', 'index': '0.0', 'children': [{'name': 'somar_cinco', 'type': 'function', 'index': '0.0.0', 'children': []}, {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.0.1', 'children': []}]}, {'name': 'Map', 'type': 'Map', 'index': '0.1', 'children': [{'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'children': []}, {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'children': []}, {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'children': []}]}]},
            {'type': 'start', 'parent': {'name': 'Sequence', 'type': 'Sequence', 'index': '0.0', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'somar_cinco', 'type': 'function', 'index': '0.0.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 8, 47470), 'end': None, 'n_iter': None, 'total_iter': None}},
            {'type': 'finish', 'parent': {'name': 'Sequence', 'type': 'Sequence', 'index': '0.0', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'somar_cinco', 'type': 'function', 'index': '0.0.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 8, 47470), 'end': datetime.datetime(2022, 10, 20, 11, 48, 8, 47631), 'n_iter': None, 'total_iter': None}},
            {'type': 'start', 'parent': {'name': 'Sequence', 'type': 'Sequence', 'index': '0.0', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.0.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 8, 47664), 'end': None, 'n_iter': None, 'total_iter': None}},
            {'type': 'finish', 'parent': {'name': 'Sequence', 'type': 'Sequence', 'index': '0.0', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.0.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 8, 47664), 'end': datetime.datetime(2022, 10, 20, 11, 48, 9, 48849), 'n_iter': None, 'total_iter': None}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49387), 'end': None, 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49843), 'end': None, 'n_iter': 1, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 50228), 'end': None, 'n_iter': 2, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 50571), 'end': None, 'n_iter': 3, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 51078), 'end': None, 'n_iter': 4, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 51527), 'end': None, 'n_iter': 5, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 50628), 'end': None, 'n_iter': 0, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49387), 'end': datetime.datetime(2022, 10, 20, 11, 48, 10, 50958), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 51040), 'end': None, 'n_iter': 1, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49387), 'end': datetime.datetime(2022, 10, 20, 11, 48, 10, 51217), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 51257), 'end': None, 'n_iter': 2, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49387), 'end': datetime.datetime(2022, 10, 20, 11, 48, 10, 51485), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 51525), 'end': None, 'n_iter': 4, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49387), 'end': datetime.datetime(2022, 10, 20, 11, 48, 10, 51889), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 51957), 'end': None, 'n_iter': 3, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.0', 'start': datetime.datetime(2022, 10, 20, 11, 48, 9, 49387), 'end': datetime.datetime(2022, 10, 20, 11, 48, 10, 52363), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 52422), 'end': None, 'n_iter': 5, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 51947), 'end': None, 'n_iter': 0, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 50628), 'end': datetime.datetime(2022, 10, 20, 11, 48, 11, 52278), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 52348), 'end': None, 'n_iter': 2, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 50628), 'end': datetime.datetime(2022, 10, 20, 11, 48, 11, 52440), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 52476), 'end': None, 'n_iter': 1, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 50628), 'end': datetime.datetime(2022, 10, 20, 11, 48, 11, 52568), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 52609), 'end': None, 'n_iter': 4, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 50628), 'end': datetime.datetime(2022, 10, 20, 11, 48, 11, 52862), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 52900), 'end': None, 'n_iter': 5, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.1', 'start': datetime.datetime(2022, 10, 20, 11, 48, 10, 50628), 'end': datetime.datetime(2022, 10, 20, 11, 48, 11, 53082), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'start', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 53125), 'end': None, 'n_iter': 3, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 51947), 'end': datetime.datetime(2022, 10, 20, 11, 48, 12, 53194), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 51947), 'end': datetime.datetime(2022, 10, 20, 11, 48, 12, 53498), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 51947), 'end': datetime.datetime(2022, 10, 20, 11, 48, 12, 53874), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 51947), 'end': datetime.datetime(2022, 10, 20, 11, 48, 12, 53998), 'n_iter': 0, 'total_iter': 6}},
            {'type': 'finish', 'parent': {'name': 'Map', 'type': 'Map', 'index': '0.1', 'start': None, 'end': None, 'n_iter': None, 'total_iter': None}, 'current': {'name': 'Multiplica', 'type': 'Multiplica', 'index': '0.1.2', 'start': datetime.datetime(2022, 10, 20, 11, 48, 11, 51947), 'end': datetime.datetime(2022, 10, 20, 11, 48, 12, 54325), 'n_iter': 0, 'total_iter': 6}},
        ]
        expected = {
            "header": {
                "name": "My Flow",
                "type": "Flow",
                "index": "0"
            },
            "flows": [
                {
                    "type": 'Sequence',
                    "name": "Sequence",
                    "index": "0.0",
                    "status": "S",
                    "executors": [
                        {
                            "name": "somar_cinco",
                            "type": "function",
                            "index": "0.0.0",
                            "status": "S"
                        },
                        {
                            "name": "Multiplica",
                            "type": "Multiplica",
                            "index": "0.0.1",
                            "status": "S"
                        }
                    ]
                },
                {
                    "name": "Map",
                    "type": "Map",
                    "index": "0.1",
                    "status": "S",
                    "executors": [
                        {
                            "name": "Multiplica",
                            "type": "Multiplica",
                            "index": "0.1.0",
                            "status": "S"
                        },
                        {
                            "name": "Multiplica",
                            "type": "Multiplica",
                            "index": "0.1.1",
                            "status": "S"
                        },
                        {
                            "name": "Multiplica",
                            "type": "Multiplica",
                            "index": "0.1.2",
                            "status": "S"
                        }
                    ]
                }
            ]
        }
        flow_design = FlowDesign()
        last_design = {}
        for message in messages:
            last_design = flow_design(message)
        self.assertEqual(last_design, expected)
        

        