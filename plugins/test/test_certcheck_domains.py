import pytest

from dnsmule_plugins.certcheck.domains import process_domains, spread_domain


@pytest.mark.parametrize('value,result', [
    (
            ['a.b', 'b.c', 'd.e', 'a.e'],
            ['a.b', 'b.c', 'd.e', 'a.e'],
    ),
    (
            ['a.b', '*.a.b', 'a.b', 'b.c.e'],
            ['a.b', 'b.c.e', 'c.e'],
    )
])
def test_process_domains(value, result):
    assert set(process_domains(value)) == set(result), 'Unexpected result'


def test_spread_domain_skips_tld():
    assert [*spread_domain('.fi')] == [], 'Failed to skip TLD'


def test_spread_domain_short():
    assert [*spread_domain('a.fi')] == ['a.fi'], 'Failed to short'


def test_spread_domain():
    assert [*spread_domain('a.b.c.fi')] == ['c.fi', 'b.c.fi', 'a.b.c.fi'], 'Failed to produce all domains'
