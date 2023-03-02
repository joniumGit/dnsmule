import asyncio

import pytest

from _async import async_test
from dnsmule.utils.async_utils import BoundedWorkQueue, ProgressReportingBoundedWorkQueue


@pytest.fixture
def create_item():
    def creator(return_value, wait: float = None):
        async def item():
            if wait:
                # Adjust this to run tests faster, but with less accuracy
                await asyncio.sleep(wait / 100)
            return return_value if not callable(return_value) else return_value()

        return item()

    yield creator


@async_test
async def test_queue_results(create_item):
    """Tests return order without limiting bound
    """
    queue = BoundedWorkQueue(
        [
            create_item(1),
            create_item(2, wait=.3),
            create_item(3, wait=.1),
        ],
        bound=10_000,
    )
    assert (await queue.complete()) == [1, 3, 2], 'Wrong order'


@async_test
async def test_queue_results_bounded_return_order_1(create_item):
    """Tests return order on bounded queue

    State:
    22233
    1111

    Result: 2, 1, 3
    """
    queue = BoundedWorkQueue(
        [
            create_item(1, wait=.4),
            create_item(2, wait=.3),
            create_item(3, wait=.2),
        ],
        bound=2,
    )
    assert (await queue.complete()) == [2, 1, 3], 'Wrong order on bounded'


@async_test
async def test_queue_results_return_order_2(create_item):
    """Tests return order on bounded queue when one task takes long

    State:
    111111
    2233

    Result: 2, 3, 1
    """
    queue = BoundedWorkQueue(
        [
            create_item(2, wait=.6),
            create_item(1, wait=.2),
            create_item(3, wait=.2),
        ],
        bound=2,
    )
    assert (await queue.complete()) == [1, 3, 2], 'Wrong order on bounded queue'


@async_test
async def test_queue_results_bounded_reporting(create_item):
    """Tests return order on bounded queue
    """
    from collections import deque

    progress_queue = deque([25., 50., 75., 100.])

    async def listener(progress: float):
        assert progress == progress_queue.popleft(), 'Queue listener received the wrong progress'

    queue = ProgressReportingBoundedWorkQueue(
        [
            create_item(1, wait=.1),
            create_item(2, wait=.3),
            create_item(3, wait=.1),
            create_item(4, wait=.2),
        ],
        bound=2,
        listener=listener,
    )
    assert await queue.complete() == [1, 3, 2, 4], 'Queue did not complete'


@async_test
async def test_queue_results_reporting_without_listener(create_item):
    queue = ProgressReportingBoundedWorkQueue(
        [
            create_item(1),
            create_item(2, wait=.1),
        ],
        bound=1,
        listener=None,
    )

    assert await queue.complete() == [1, 2], 'Queue did not run without listener'


@async_test
async def test_queue_cancelling(create_item):
    def raise_exception():
        raise ValueError()

    queue = BoundedWorkQueue(
        [
            create_item(raise_exception, wait=.1),
            create_item(raise_exception, wait=.3),
            create_item(raise_exception, wait=.1),
            create_item(raise_exception, wait=.2),
        ],
        bound=2,
    )

    await queue.cancel()


@async_test
async def test_queue_item_raised_cancelling_all(create_item):
    def raise_exception():
        raise ValueError()

    def raise_exception_2():
        assert False, 'Should never get here'

    queue = BoundedWorkQueue(
        [
            create_item(raise_exception, wait=.1),
            create_item(raise_exception_2, wait=.3),
        ],
        bound=1,
    )

    with pytest.raises(ValueError):
        await queue.complete()


@async_test
async def test_queue_results_bounded_return_order_1_iterating(create_item):
    """Tests return order on bounded queue when iterating

    State:
    22233
    111

    Result: [2, 1], [3]
    """
    queue = BoundedWorkQueue(
        [
            create_item(1, wait=.3),
            create_item(2, wait=.3),
            create_item(3, wait=.2),
        ],
        bound=2,
    )

    # Use sets as it is hard to control the in-set order
    assert [set(value) async for value in queue.iterate()] == [{2, 1}, {3}], 'Wrong order on bounded iteration'
