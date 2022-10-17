from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, List

class FlowThreads:
    def __init__(self, task_callable: Callable, thread_iter: List[Any], args: List[Any] = [], n_workers = 10) -> None:
        self._task_callable = task_callable
        self._thread_iter = thread_iter
        self._args = args
        self._n_workers = n_workers
    def run(self):
        with ThreadPoolExecutor(max_workers=self._n_workers) as executor:
            futures = [executor.submit(self._task_callable, item, self._args) for item in self._thread_iter]
            return [future.result() for future in futures]
            