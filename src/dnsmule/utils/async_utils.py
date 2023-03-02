import asyncio as aio

from collections import deque
from typing import Iterable, Coroutine, Any, TypeVar, Generic, Deque, List, Callable

T = TypeVar('T')


class BoundedWorkQueue(Generic[T]):
    waiting: Deque[Coroutine[Any, Any, T]]
    tasks: Deque[aio.Task[T]]
    results: Deque[T]
    bound: int

    def __init__(self, items: Iterable[Coroutine[Any, Any, T]], bound: int):
        self.waiting = deque(items)
        self.tasks = deque()
        self.results = deque()
        self.bound = bound

    def _populate(self):
        if self.waiting:
            for _ in range(self.bound - len(self.tasks)):
                if self.waiting:
                    self.tasks.append(aio.create_task(self.waiting.popleft()))
                else:
                    break

    async def _wait_for_next(self):
        try:
            done, pending = await aio.wait(self.tasks, return_when=aio.FIRST_COMPLETED)
            self.tasks = deque(pending)
            self.results.extend(t.result() for t in done)
        except:
            await self.cancel()
            raise

    async def iterate(self):
        while self.tasks or self.waiting:
            self._populate()
            await self._wait_for_next()
            _results = self.results
            self.results = deque()
            yield [*_results]

    async def complete(self) -> List[T]:
        while self.tasks or self.waiting:
            self._populate()
            await self._wait_for_next()
        return [*self.results]

    async def cancel(self):
        import contextlib
        remaining = aio.gather(*self.tasks, *self.waiting, return_exceptions=False)
        remaining.cancel()
        with contextlib.suppress(aio.CancelledError):
            await remaining


class ProgressReportingBoundedWorkQueue(BoundedWorkQueue[T]):
    progress: float

    def __init__(self, *args, listener: Callable[[float], Coroutine[Any, Any, Any]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress = 0.
        self._max = len(self.waiting)
        self._listener = listener

    async def _wait_for_next(self):
        await super()._wait_for_next()
        self.progress = len(self.results) / self._max * 100
        if self._listener is not None:
            await self._listener(self.progress)


__all__ = [
    'BoundedWorkQueue',
    'ProgressReportingBoundedWorkQueue',
]
