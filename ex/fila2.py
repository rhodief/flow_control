from ast import arg
#from queue import Queue
from multiprocessing import Queue
import random
from multiprocessing import Process
import time
import os
from typing import Any 

class MeuCallable:
    def __init__(self, valor) -> None:
        self._valor = valor
    def __call__(self) -> Any:
        time.sleep(random.random())
        return f'{self._valor}*'


class Worker:
    def __init__(self) -> None:
        self.running = True
    def __call__(self, queue: Queue, result_queue: Queue) -> Any:
        while self.running:
            k, task = queue.get()
            if task is None: 
                self.running = False
            else:
                result_queue.put((k, task()))
    

class WorkerQueue:
    def __init__(self, n_workers: int = 10) -> None:
        self._n_workers = n_workers
        self._queue: Queue = Queue()
        self._result_queue = Queue()
        self.workers = [Process(target=Worker(), args=(self._queue, self._result_queue), daemon=True) for _ in range(n_workers)]
        [_.start() for _ in self.workers]
        self._results = []
        self._counter = 0
    def __call__(self, task: MeuCallable) -> Any:
        self._queue.put((self._counter, task))
        self._counter+=1
    def pending_task_size(self):
        return self._queue.qsize()
    def finished_task_size(self):
        return self._result_queue.qsize()
    def results(self):
        [self._queue.put((0, None)) for _ in range(self._n_workers)]
        for w in self.workers:
            w.join()
        while self._result_queue.qsize() > 0:
            self._results.append(self._result_queue.get())
        self._results.sort(key=lambda x: x[0])
        return [e for k, e in self._results]
        
        
        

wq = WorkerQueue()
for i in range(100):
    wq(MeuCallable(i))
print('Pendentes', wq.pending_task_size())
print('Resultado', wq.results())
print('Resultado', len(wq.results()))


exit()

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

processos = []
for i in range(100):
    e = MeuCallable(i)
    p = Process(target=e)
    p.start()
    processos.append((e, p))

for e, p in processos:
    p.join()
for e, p in processos:
    print(e._result)

exit()

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

