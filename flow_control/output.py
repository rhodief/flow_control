
from typing import Any, Tuple
import threading
from queue import Queue

class Broker:
    def __init__(self, q:Queue) -> None:
        self._queue = q
    def put(self, msg):
        self._queue.put(msg)
    def get(self):
        return self._queue.get()
    def done(self):
        return self._queue.task_done()
    def block(self):
        return self._queue.join()

    
class PrinterWorker():
    def __call__(self, broker) -> Any:
        while True:
            item  = broker.get()
            print(f'Mensagem: ', item)
            broker.done()
            
class SuperPrinter():
    '''
    This is responsable to expose the application logs.
    '''
    def __init__(self, broker: Broker, exposingWorker: PrinterWorker) -> None:
        self._broker = broker
        self._bd = {}
        self._thread = threading.Thread(target=exposingWorker, args=(self._broker,), daemon=True)        
    def watch(self):
        self._thread.start()
    def block(self):
        self._broker.block()
    
            
