import datetime
from asyncio import sleep
from ipaddress import IPv4Network

import pytest

from _async import async_test
from dnsmule import Record, RRType
from dnsmule_plugins.ipranges.ranges import IPvXRange
from dnsmule_plugins.ipranges.rule import IpRangeChecker


@async_test
async def test_ipranges_task():
    checker = IpRangeChecker(providers=[])

    assert checker._last_fetch is None, 'Spawned with fetch time'

    async def fetch_ranges():
        await sleep(.1)

    checker.fetch_ranges = fetch_ranges

    await checker.check_fetch()

    assert not hasattr(checker, '_task'), 'Task did not get deleted'
    assert checker._last_fetch is not None, 'Missing fetch time'


@async_test
async def test_ipranges_task_if_task_exists():
    checker = IpRangeChecker(providers=[])
    called = []

    async def fetch_ranges():
        called.append('fetch')

    checker._task = fetch_ranges()

    await checker.check_fetch()
    assert called == ['fetch'], 'Task was not awaited'


@async_test
async def test_ipranges_task_if_not_recent():
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


def test_ipranges_unknown_provider():
    with pytest.raises(AttributeError):
        IpRangeChecker(providers=['adwadawdawdawdwad'])


@async_test
async def test_ipranges_provider_tags():
    rule = IpRangeChecker(providers=[], name='test_rule')
    rule._provider_ranges['test_provider'] = [IPvXRange(
        address=IPv4Network('127.0.0.0/31'),
        region='test_region',
        service='test_service',
    )]
    r = Record('', RRType.A, '127.0.0.1')
    rule._last_fetch = datetime.datetime.now()
    await rule(r)
    assert 'IP::RANGES::TEST_RULE::TEST_SERVICE::TEST_REGION' in r.result()


@async_test
async def test_ipranges_provider_no_tags_if_no_match():
    rule = IpRangeChecker(providers=[], name='test_rule')
    rule._provider_ranges['test_provider'] = [IPvXRange(
        address=IPv4Network('128.0.0.0/24'),
        region='test_region',
        service='test_service',
    )]
    r = Record('', RRType.A, '127.0.0.1')
    rule._last_fetch = datetime.datetime.now()
    await rule(r)
    assert len(r.result().tags) == 0, 'Had a tag'


@async_test
async def test_ipranges_provider_empty_provider_fetch_ok():
    rule = IpRangeChecker(providers=[], name='test_rule')
    await rule.check_fetch()
    assert rule._last_fetch is not None, 'Failed fetch'
