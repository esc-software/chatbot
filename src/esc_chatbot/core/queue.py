import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock, Thread
from typing import Any, Callable

from ..config import settings


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    status: TaskStatus
    created_at: float
    processed_at: float | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class ChatQueue:
    def __init__(self, process_fn: Callable[[dict[str, Any], str], dict[str, Any]]) -> None:
        self._process_fn = process_fn
        self._queue: deque[tuple[str, dict[str, Any], str]] = deque()
        self._tasks: dict[str, Task] = {}
        self._lock = Lock()
        self._max_size = settings.queue_max_size
        self._running = True

        for _ in range(settings.queue_workers):
            t = Thread(target=self._worker_loop, daemon=True)
            t.start()

    def enqueue(self, params: dict[str, Any], ip: str) -> str | None:
        if len(self._queue) >= self._max_size:
            return None

        task_id = uuid.uuid4().hex[:12]
        with self._lock:
            self._tasks[task_id] = Task(
                id=task_id,
                status=TaskStatus.PENDING,
                created_at=time.time(),
            )
            self._queue.append((task_id, params, ip))
        return task_id

    def get_result(self, task_id: str) -> Task | None:
        with self._lock:
            return self._tasks.get(task_id)

    def stats(self) -> dict[str, int]:
        with self._lock:
            statuses: dict[str, int] = {}
            for t in self._tasks.values():
                statuses[t.status.value] = statuses.get(t.status.value, 0) + 1
            return {
                "queue_size": len(self._queue),
                **statuses,
            }

    def _worker_loop(self) -> None:
        while self._running:
            try:
                task_id, params, ip = self._queue.popleft()
            except IndexError:
                time.sleep(0.05)
                continue

            with self._lock:
                self._tasks[task_id].status = TaskStatus.PROCESSING

            try:
                result = self._process_fn(params, ip)
                with self._lock:
                    task = self._tasks[task_id]
                    task.status = TaskStatus.DONE
                    task.result = result
                    task.processed_at = time.time()
            except Exception as exc:
                with self._lock:
                    task = self._tasks[task_id]
                    task.status = TaskStatus.FAILED
                    task.error = str(exc)
                    task.processed_at = time.time()
