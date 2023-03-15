import pytest

from _async import async_test
from dnsmule import DNSMule, Record, RRType
from dnsmule_plugins.ptrscan.rule import PTRScan


def test_ptrscan_init_no_backend():
    r = PTRScan()
    assert not hasattr(r, '_mule'), 'Had mule on create'


def test_ptrscan_creator_appends_backend():
    marker = object()
    creator = PTRScan.creator(marker)
    r = creator()
    assert r._mule is marker, 'Failed to set mule to marker'


def test_ptrscan_reverses_ipv4():
    assert PTRScan.reverse_query('127.0.0.1') == '1.0.0.127.in-addr.arpa'


def test_ptrscan_reverses_ipv6():
    res = 'b.a.9.8.7.6.5.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'
    assert PTRScan.reverse_query('2001:db8::567:89ab') == res


@async_test
async def test_ptrscan_returns_different_result():
    """This is to prevent dupes in data
    """
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    record = Record('example.com', RRType.A, '127.0.0.1')
    result = await r(record)

    assert result is not record.result(), 'Produced same result'


@async_test
async def test_ptrscan_with_mock_empty_result():
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    async def run_single(domain, rtype):
        assert domain == '1.0.0.127.in-addr.arpa'
        assert rtype == RRType.PTR
        for _ in []:
            yield

    mule.backend.run_single = run_single

    # This also checks dupes
    await r(Record('example.com', RRType.A, '127.0.0.1'))
    result = await r(Record('example.com', RRType.A, '127.0.0.1'))

    assert len(result.tags) == 0, 'Identified empty'
    assert 'resolvedPointers' not in result.data, 'Added pointers'


@async_test
async def test_ptrscan_with_mock():
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    async def run_single(domain, rtype):
        assert domain == '1.0.0.127.in-addr.arpa'
        assert rtype == RRType.PTR
        yield Record('1.0.0.127.in-addr.arpa', RRType.PTR, '127.0.0.1.provider.com')

    mule.backend.run_single = run_single

    # This also checks dupes
    await r(Record('example.com', RRType.A, '127.0.0.1'))
    result = await r(Record('example.com', RRType.A, '127.0.0.1'))

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
@async_test
async def test_ptrscan_with_mock_no_dupes_and_ptr_appended(ptr):
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    async def run_single(*_):
        yield Record('1.0.0.127.in-addr.arpa', RRType.PTR, ptr)

    mule.backend.run_single = run_single

    # Adds ptr
    record = Record('example.com', RRType.A, '127.0.0.1')
    record.result().data['resolvedPointers'] = ['sample-127.0.0.1.provider.com']

    result = await r(record)
    assert result.data['resolvedPointers'] == [ptr], 'Failed to prevent duplicate'


@async_test
async def test_ptrscan_with_mock_ptr_no_match():
    mule = DNSMule.make()
    r = PTRScan.creator(mule)(name='test')

    async def run_single(*_):
        yield Record('1.0.0.127.in-addr.arpa', RRType.PTR, 'aaaa')

    mule.backend.run_single = run_single

    record = Record('example.com', RRType.A, '127.0.0.1')

    result = await r(record)
    assert len(result.tags) == 0, 'Identified'
    assert result.data['resolvedPointers'] == ['aaaa'], 'Failed to add ptr'
