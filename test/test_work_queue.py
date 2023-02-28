import asyncio

from _async import async_test
from dnsmule.utils.asyncio import BoundedWorkQueue, ProgressReportingBoundedWorkQueue


@async_test
async def test_queue_results():
    """Tests return order without limiting bound
    """

    async def item_1():
        return 1

    async def item_2():
        await asyncio.sleep(0.3)
        return 2

    async def item_3():
        await asyncio.sleep(0.1)
        return 3

    queue = BoundedWorkQueue([item_1(), item_2(), item_3()], bound=10_000)
    assert (await queue.complete()) == [1, 3, 2]


@async_test
async def test_queue_results_bounded_return_order_1():
    """Tests return order on bounded queue

    State:
    22233
    1111

    Result: 2, 1, 3
    """

    async def item_1():
        await asyncio.sleep(0.4)
        return 1

    async def item_2():
        await asyncio.sleep(0.3)
        return 2

    async def item_3():
        await asyncio.sleep(0.2)
        return 3

    queue = BoundedWorkQueue([item_1(), item_2(), item_3()], bound=2)
    assert (await queue.complete()) == [2, 1, 3]


@async_test
async def test_queue_results_return_order_2():
    """Tests return order on bounded queue when one task takes long

    State:
    111111
    2233

    Result: 2, 3, 1
    """

    async def item_1():
        await asyncio.sleep(0.6)
        return 1

    async def item_2():
        await asyncio.sleep(0.2)
        return 2

    async def item_3():
        await asyncio.sleep(0.2)
        return 3

    queue = BoundedWorkQueue([item_2(), item_1(), item_3()], bound=2)
    assert (await queue.complete()) == [2, 3, 1]


@async_test
async def test_queue_results_bounded_reporting():
    """Tests return order on bounded queue
    """
    from collections import deque

    async def item_1():
        return 1

    async def item_2():
        return 2

    async def item_3():
        return 3

    async def item_4():
        return 4

    progress_queue = deque([25., 50., 75., 100.])

    async def listener(progress: float):
        assert progress == progress_queue.popleft()

    queue = ProgressReportingBoundedWorkQueue(
        [item_1(), item_2(), item_3(), item_4()],
        bound=1,
        listener=listener,
    )

    await queue.complete()
