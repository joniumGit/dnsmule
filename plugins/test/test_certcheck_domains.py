import pytest

from dnsmule_plugins.certcheck.domains import lagging_filter, filter_locally_unique, process_domains, spread_domain


@pytest.mark.parametrize('i,lag,result', [
    (
            ['a', 'a', 'a', 'b', 'b'],
            1,
            ['a', 'b'],
    ),
    (
            ['a', 'b', 'c', 'a', 'b', 'c'],
            3,
            ['a', 'b', 'c'],
    ),
    (
            ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd'],
            3,
            ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd'],
    ),
    (
            ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd'],
            2,
            ['a', 'b', 'c', 'd', 'a', 'b', 'c', 'd'],
    ),
    (
            ['a', 'b', 'c', 'd', 'a', 'a', 'b', 'b'],
            2,
            ['a', 'b', 'c', 'd', 'a', 'b'],
    ),
])
def test_lagging_filter(i, lag, result):
    assert [*filter_locally_unique(i, lag=lag)] == result, 'Did not filter'


@pytest.mark.parametrize('lag', [
    0,
    -1,
])
def test_lagging_filter_value_error(lag):
    with pytest.raises(ValueError):
        lagging_filter(lag)


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
