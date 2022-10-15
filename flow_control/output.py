
from queue import Queue
from typing import Tuple

from flow_control.execution_control import ExecutionFamily


class SuperLogger:
    def __init__(self, queue: Queue) -> None:
        self._queue = queue
    def get(self) -> Tuple[str, ExecutionFamily]:
        return self._queue.get()