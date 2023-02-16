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
        done, pending = await aio.wait(self.tasks, return_when=aio.FIRST_COMPLETED)
        self.tasks = deque(pending)
        self.results.extend(t.result() for t in done)

    async def complete(self) -> List[T]:
        while self.tasks or self.waiting:
            self._populate()
            await self._wait_for_next()
        return [*self.results]

    async def cancel(self):
        import contextlib
        for coro in self.waiting:
            coro.close()
        remaining = aio.gather(*self.tasks, return_exceptions=True)
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


def map_async_interactive(
        work: Iterable[Coroutine[Any, Any, T]],
        bound: int,
        listener: Callable[[float], Coroutine[Any, Any, Any]] = None,
):
    """Use asyncio to map coroutines using a bounded queue

    note: This is not usable inside already async programs.

    note: This will catch a KeyboardInterrupt as the work cancellation call and will not propagate it
    """
    from asyncio import new_event_loop

    if listener is None:
        queue = BoundedWorkQueue(work, bound)
    else:
        queue = ProgressReportingBoundedWorkQueue(work, bound, listener=listener)

    loop = new_event_loop()
    try:
        result = loop.run_until_complete(queue.complete())
    except KeyboardInterrupt:
        loop.run_until_complete(queue.cancel())
        loop.run_until_complete(loop.shutdown_asyncgens())
        result = [*queue.results]
    finally:
        loop.close()

    return result


__all__ = [
    'BoundedWorkQueue',
    'ProgressReportingBoundedWorkQueue',
    'map_async_interactive',
]
