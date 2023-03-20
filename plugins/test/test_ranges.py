import os
from ipaddress import IPv4Network, IPv4Address, IPv6Network

import pytest

from dnsmule_plugins.ipranges import ranges, rule


def test_ipvx_has_address_str():
    r = ranges.IPvXRange(address=IPv4Network('127.0.0.0/24'), service='test', region='test-region')
    assert '127.0.0.20' in r


def test_ipvx_has_ipv6_address_str():
    r = ranges.IPvXRange(address=IPv6Network('2001:db8:a::/64'), service='test', region='test-region')
    assert '2001:db8:a::123' in r


def test_ipvx_has_address():
    r = ranges.IPvXRange(address=IPv4Network('127.0.0.0/24'), service='test', region='test-region')
    assert IPv4Address('127.0.0.20') in r


def test_ipvx_has_no_network():
    r = ranges.IPvXRange(address=IPv4Network('127.0.0.0/24'), service='test', region='test-region')
    assert IPv4Network('127.0.0.0/31') not in r


def test_ipvx_has_no_proto_mismatch():
    r = ranges.IPvXRange(address=IPv4Network('127.0.0.0/24'), service='test', region='test-region')
    assert '2001:db8:a::123' not in r


def test_ipvx_network_raises():
    r = ranges.IPvXRange(address=IPv4Network('127.0.0.0/24'), service='test', region='test-region')
    assert '127.0.0.0/16' not in r


def test_rule_fetching_failure_cancels_tasks():
    r = rule.IpRangeChecker(providers=[])
    r.providers = ['a', 'b']  # Prevents throw on init

    def fetch_provider(key):
        if key == 'b':
            raise ValueError()

    r.fetch_provider = fetch_provider

    r.fetch_ranges()


PROVIDERS = [
    'google',
    'microsoft',
    'amazon',
]


@pytest.mark.skipif(os.getenv('FETCH_RANGES', 'false') != 'true', reason='Range fetch disabled')
class TestRangesFetching:

    @pytest.mark.parametrize('provider', PROVIDERS)
    def test_fetch_ranges(self, provider):
        assert len(getattr(ranges, f'fetch_{provider}_ip_ranges')()) != 0, f'Failed to fetch {provider} ranges'

    def test_fetch_with_plugin(self):
        r = rule.IpRangeChecker(providers=PROVIDERS)
        r.check_fetch()
        assert len(r._provider_ranges) != 0, 'Failed to fetch ranges'
