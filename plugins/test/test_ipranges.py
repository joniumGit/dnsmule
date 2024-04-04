import datetime
from ipaddress import IPv4Network
from time import sleep

import pytest

from dnsmule_plugins.ipranges.iprange import IPvXRange
from dnsmule_plugins.ipranges.rule import IpRangeChecker


def test_fetching_add_last_fetch():
    checker = IpRangeChecker(providers=[])

    assert checker._last_fetch is None, 'Spawned with fetch time'

    def fetch_ranges():
        sleep(.1)

    checker.fetch_ranges = fetch_ranges

    checker.check_fetch()

    assert checker._last_fetch is not None, 'Missing fetch time'


def test_context_should_fetch_on_enter():
    checker = IpRangeChecker(providers=[])
    called = []

    def fetch_ranges():
        called.append('fetch')

    checker.fetch_ranges = fetch_ranges

    with checker:
        pass

    assert called == ['fetch'], 'Not fetched'


def test_context_should_not_fetch_on_enter_if_recently_fetched():
    checker = IpRangeChecker(providers=[])
    called = []

    def fetch_ranges():
        called.append('fetch')

    checker.fetch_ranges = fetch_ranges
    checker._last_fetch = datetime.datetime.now()

    with checker:
        pass

    assert called == [], 'Fetched twice'


def test_unknown_provider():
    with pytest.raises(Exception):
        IpRangeChecker(providers=['adwadawdawdawdwad'])


def test_provider_tags(record, result):
    rule = IpRangeChecker(providers=[])
    rule._provider_ranges['test_provider'] = [IPvXRange(
        address=IPv4Network('127.0.0.0/31'),
        region='test_region',
        service='test_service',
    )]
    rule._last_fetch = datetime.datetime.now()
    rule(record, result)
    assert 'IP::RANGES::TEST_SERVICE::TEST_REGION' in result.tags


def test_provider_no_tags_if_no_match(record, result):
    rule = IpRangeChecker(providers=[])
    rule._provider_ranges['test_provider'] = [IPvXRange(
        address=IPv4Network('128.0.0.0/24'),
        region='test_region',
        service='test_service',
    )]
    rule._last_fetch = datetime.datetime.now()
    rule(record, result)
    assert len(result.tags) == 0, 'Had a tag'


def test_provider_empty_provider_fetch_ok():
    rule = IpRangeChecker(providers=[])
    rule.check_fetch()
    assert rule._last_fetch is not None, 'Failed fetch'


def test_fetcher_for_provider(monkeypatch):
    sentinel = object()
    with monkeypatch.context() as m:
        from dnsmule_plugins.ipranges.providers import Providers
        m.setitem(Providers._mapping, 'mock', lambda: sentinel)
        checker = IpRangeChecker(providers=['mock'])
        checker.fetch_provider('mock')
        assert checker._provider_ranges['mock'] is sentinel, 'Failed to get provider from package or failed to call'
