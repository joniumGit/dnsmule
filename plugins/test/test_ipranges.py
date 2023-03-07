import datetime
from asyncio import sleep

from _async import async_test
from dnsmule_plugins.ipranges.rule import IpRangeChecker


@async_test
async def test_fetching_task():
    checker = IpRangeChecker(providers=[])

    assert checker._last_fetch is None, 'Spawned with fetch time'

    async def fetch_ranges():
        await sleep(.1)

    checker.fetch_ranges = fetch_ranges

    await checker.check_fetch()

    assert not hasattr(checker, '_task'), 'Task did not get deleted'
    assert checker._last_fetch is not None, 'Missing fetch time'


@async_test
async def test_fetching_task_if_task_exists():
    checker = IpRangeChecker(providers=[])
    called = []

    async def fetch_ranges():
        called.append('fetch')

    checker._task = fetch_ranges()

    await checker.check_fetch()
    assert called == ['fetch'], 'Task was not awaited'


@async_test
async def test_fetching_task_if_not_recent():
    """Visible from coverage only
    """
    checker = IpRangeChecker(providers=[])
    called = []

    async def fetch_ranges():
        await sleep(.1)
        called.append('fetch')

    def start_fetch():
        checker._task = fetch_ranges()

    checker.start_fetching = start_fetch

    checker._last_fetch = datetime.datetime.now()
    await checker.check_fetch()
    assert len(called) == 0, 'Task was called'

    checker._last_fetch = checker._last_fetch - datetime.timedelta(days=1)
    await checker.check_fetch()
    assert len(called) == 1, 'Task was not called'
