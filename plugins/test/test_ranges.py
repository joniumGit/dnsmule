import os
from ipaddress import IPv4Network, IPv4Address, IPv6Network

import pytest

from dnsmule_plugins.ipranges import rule
from dnsmule_plugins.ipranges.iprange import IPvXRange
from dnsmule_plugins.ipranges.providers import Providers


def test_ipvx_has_address_str():
    r = IPvXRange(
        address=IPv4Network('127.0.0.0/24'),
        service='test',
        region='test-region',
    )
    assert '127.0.0.20' in r


def test_ipvx_has_ipv6_address_str():
    r = IPvXRange(
        address=IPv6Network('2001:db8:a::/64'),
        service='test',
        region='test-region',
    )
    assert '2001:db8:a::123' in r


def test_ipvx_has_address():
    r = IPvXRange(
        address=IPv4Network('127.0.0.0/24'),
        service='test',
        region='test-region',
    )
    assert IPv4Address('127.0.0.20') in r


def test_ipvx_has_no_network():
    r = IPvXRange(
        address=IPv4Network('127.0.0.0/24'),
        service='test',
        region='test-region',
    )
    assert IPv4Network('127.0.0.0/31') not in r


def test_ipvx_has_no_proto_mismatch():
    r = IPvXRange(
        address=IPv4Network('127.0.0.0/24'),
        service='test',
        region='test-region',
    )
    assert '2001:db8:a::123' not in r


def test_ipvx_network_raises():
    r = IPvXRange(
        address=IPv4Network('127.0.0.0/24'),
        service='test',
        region='test-region',
    )
    assert '127.0.0.0/16' not in r


def test_rule_fetching_failure_cancels_tasks():
    r = rule.IpRangeChecker(providers=[])
    r.providers = ['a', 'b']  # Prevents throw on init

    def fetch_provider(key):
        if key == 'b':
            raise ValueError()

    r.fetch_provider = fetch_provider

    with r:
        pass


@pytest.mark.skipif(os.getenv('FETCH_RANGES', 'false') != 'true', reason='Range fetch disabled')
class TestRangesFetching:

    @pytest.fixture(params=Providers.all())
    def provider(self, request):
        yield request.param

    def test_fetch_available(self, provider):
        assert Providers.available(provider), f'Failed to fetch {provider} ranges'

    def test_fetch_ranges(self, provider):
        assert len(Providers.fetch(provider)) != 0, f'Failed to fetch {provider} ranges'
