from ast import arg
#from queue import Queue
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor
import random
from multiprocessing import Process
import time
import os
from typing import Any

class MeuCallable:
    def __init__(self, valor) -> None:
        self._valor = valor
        self._result = None
    def __call__(self, novo_valor) -> Any:
        print(self._valor, novo_valor)
        self._result = f'{novo_valor}*'
        return self._result

def producer(_queue: Queue, i: str):
    #time.sleep(1)
    _queue.put((i, MeuCallable(i)))
    #print('Produzi', _queue.qsize())
    return i

def consumer_worker(_queue: Queue):
    i, callable = _queue.get()
    r = callable(i)
    print('Worker result', i, r, callable._result)
    #_queue.task_done()

q = Queue()

def mega_producer(_queue: Queue, p: str):
    print('Mega Prod', p, os.getpid())
    return [producer(_queue, f'{p}.{i}') for i in range(10)]


p1 = Process(target=mega_producer, args=[q, 'p1'])

p2 = Process(target=mega_producer, args=[q, 'p2'])

p3 = Process(target=mega_producer, args=[q, 'p3'])

p1.start()
p2.start()
p3.start()

print('Iniciando consumer...')
while True:
    print(f'Tamanho: {q.qsize()}')
    consumer_worker(q)

