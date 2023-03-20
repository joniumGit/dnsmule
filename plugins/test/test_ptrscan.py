from typing import Any

import pytest

from dnsmule import DNSMule, Record, RRType, Domain
from dnsmule_plugins.ptrscan.rule import PTRScan


def test_init_no_backend():
    r = PTRScan()
    assert not hasattr(r, '_mule'), 'Had mule on create'


def test_creator_appends_backend():
    marker: Any = object()
    creator = PTRScan.creator(marker)
    r = creator()
    assert r._mule is marker, 'Failed to set mule to marker'


def test_reverses_ipv4():
    assert PTRScan.reverse_query('127.0.0.1') == '1.0.0.127.in-addr.arpa'


def test_reverses_ipv6():
    res = 'b.a.9.8.7.6.5.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'
    assert PTRScan.reverse_query('2001:db8::567:89ab') == res


def test_with_mock_empty_result():
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    def run_single(domain, rtype):
        assert domain == '1.0.0.127.in-addr.arpa'
        assert rtype == RRType.PTR
        for _ in []:
            yield

    mule.backend.single = run_single

    # This also checks dupes
    r(Record(Domain('example.com'), RRType.A, '127.0.0.1'))
    result = r(Record(Domain('example.com'), RRType.A, '127.0.0.1'))

    assert len(result.tags) == 0, 'Identified empty'
    assert 'resolvedPointers' not in result.data, 'Added pointers'


def test_with_mock():
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    def run_single(domain, rtype):
        assert domain == '1.0.0.127.in-addr.arpa'
        assert rtype == RRType.PTR
        yield Record(Domain('1.0.0.127.in-addr.arpa'), RRType.PTR, '127.0.0.1.provider.com')

    mule.backend.single = run_single

    # This also checks dupes
    r(Record(Domain('example.com'), RRType.A, '127.0.0.1'))
    result = r(Record(Domain('example.com'), RRType.A, '127.0.0.1'))

    assert len(result.tags) != 0, 'Failed to identify'
    assert result.tags.pop() == 'IP::PTR::TEST::PROVIDER.COM'
    assert result.data['resolvedPointers'] == ['127.0.0.1.provider.com']


@pytest.mark.parametrize('ptr', [
    '127-0-0-1-provider.com',
    '127.0.0.1.provider.com',
    '1.0.0.127.provider.com',
    '127-0-0-1.provider.com',
    '1-0-0-127.provider.com',
    'cdn-127-0-0-1.provider.com',
    'cdn.127.0.0.1.provider.com',
])
def test_with_mock_no_dupes_and_ptr_appended(ptr):
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    def run_single(*_):
        yield Record(Domain('1.0.0.127.in-addr.arpa'), RRType.PTR, ptr)

    mule.backend.single = run_single

    # Adds ptr
    record = Record(Domain('example.com'), RRType.A, '127.0.0.1')
    record.result.data['resolvedPointers'] = ['sample-127.0.0.1.provider.com', 'sample-127.0.0.1.provider.com']

    r(record)
    result = r(record)

    assert len(result.data['resolvedPointers']) == 2, 'Failed to prevent or remove duplicate'


def test_with_mock_ptr_no_match():
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    def run_single(*_):
        yield Record(Domain('1.0.0.127.in-addr.arpa'), RRType.PTR, 'aaaa')

    mule.backend.single = run_single

    record = Record(Domain('example.com'), RRType.A, '127.0.0.1')

    result = r(record)
    assert len(result.tags) == 0, 'Identified'
    assert result.data['resolvedPointers'] == ['aaaa'], 'Failed to add ptr'
