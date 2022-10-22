import unittest
from flow_control.output import FlowDesign
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, composite, SearchStrategy, text
import datetime

class TestSuperPrinterWorker(unittest.TestCase):
    def test_terminal_dict(self):
        messages = [
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
        #self.assertEqual(last_design, expected)
        

        