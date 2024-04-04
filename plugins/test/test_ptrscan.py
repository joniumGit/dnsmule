import pytest

from dnsmule import DNSMule, Record, RRType, Domain, Rules
from dnsmule import DictStorage, DataBackend
from dnsmule_plugins.ptrscan.rule import PTRScan


def test_init_no_backend():
    r = PTRScan()
    assert not hasattr(r, '_mule'), 'Had mule on create'


def test_reverses_ipv4():
    assert PTRScan.reverse_query('127.0.0.1') == '1.0.0.127.in-addr.arpa'


def test_reverses_ipv6():
    res = 'b.a.9.8.7.6.5.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'
    assert PTRScan.reverse_query('2001:db8::567:89ab') == res


def test_with_mock_empty_result(record, result):
    def run_single(domain, rtype):
        assert domain == '1.0.0.127.in-addr.arpa'
        assert rtype == RRType.PTR
        for _ in []:
            yield

    mule = DNSMule(
        storage=DictStorage(),
        backend=DataBackend(),
        rules=Rules()
    )
    mule.backend.scan = run_single

    rule = PTRScan()
    mule.rules.register(RRType.A, rule)

    mule._run_rule(rule, record, result)
    assert len(result.tags) == 0, 'Identified empty'
    assert 'resolvedPointers' not in result.data, 'Added pointers'


def test_with_mock(record, result):
    def run_single(domain, rtype):
        assert domain == '1.0.0.127.in-addr.arpa'
        assert rtype == RRType.PTR
        yield Record(
            Domain('1.0.0.127.in-addr.arpa'),
            RRType.PTR,
            '127.0.0.1.provider.com',
        )

    mule = DNSMule(
        storage=DictStorage(),
        backend=DataBackend(),
        rules=Rules()
    )
    mule.backend.scan = run_single

    rule = PTRScan()
    mule.rules.register(RRType.A, rule)

    mule._run_rule(rule, record, result)
    assert len(result.tags) != 0, 'Failed to identify'
    assert result.tags.pop() == 'IP::PTR::PROVIDER.COM'
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
def test_with_mock_no_dupes_and_ptr_appended(ptr, record, result):
    def run_single(*_):
        yield Record(Domain('1.0.0.127.in-addr.arpa'), RRType.PTR, ptr)

    mule = DNSMule(
        storage=DictStorage(),
        backend=DataBackend(),
        rules=Rules()
    )
    mule.backend.scan = run_single

    rule = PTRScan()
    mule.rules.register(RRType.A, rule)

    # Adds ptr
    result.data['resolvedPointers'] = ['sample-127.0.0.1.provider.com', 'sample-127.0.0.1.provider.com']

    mule._run_rule(rule, record, result)
    assert len(result.data['resolvedPointers']) == 2, 'Failed to prevent or remove duplicate'


def test_with_mock_ptr_no_match(record, result):
    def run_single(*_):
        yield Record(Domain('1.0.0.127.in-addr.arpa'), RRType.PTR, 'aaaa')

    mule = DNSMule(
        storage=DictStorage(),
        backend=DataBackend(),
        rules=Rules()
    )
    mule.backend.scan = run_single

    rule = PTRScan()
    mule.rules.register(RRType.A, rule)

    mule._run_rule(rule, record, result)
    assert len(result.tags) == 0, 'Identified'
    assert result.data['resolvedPointers'] == ['aaaa'], 'Failed to add ptr'
