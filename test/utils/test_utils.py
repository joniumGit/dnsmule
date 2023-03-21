import pathlib

import pytest

from dnsmule.utils import *
from dnsmule.utils.domains import spread_domain


@pytest.mark.parametrize('file', [
    'sample_1.csv',
    'sample_1.txt',
])
def test_load_file(file):
    file = pathlib.Path(__file__).parent / file
    assert [*load_data(file)] == ['example.com', 'a.example.com']
    assert [*load_data(file, limit=1)] == ['example.com']
    assert [*load_data(file, limit=2)] == ['example.com', 'a.example.com']
    assert [*load_data(file, limit=-2)] == ['example.com', 'a.example.com']


@pytest.mark.parametrize('a,b,result', [
    ({'a': 1}, {'b': 1}, {'a': 1, 'b': 1}),
    ({'a': 1}, {'a': 1}, {'a': 2}),
    ({'a': [1]}, {'a': [2]}, {'a': [1, 2]}),
    ({'a': [1]}, {'a': {2}}, {'a': [1, 2]}),
    ({'a': [1]}, {'a': frozenset({2})}, {'a': [1, 2]}),
    ({'a': [1]}, {'a': tuple({2})}, {'a': [1, 2]}),
    ({'a': [1]}, {'a': {'a': 1}}, {'a': [1, {'a': 1}]}),
])
def test_lmerge_examples(a, b, result):
    lmerge(a, b)
    assert a == result


@pytest.mark.parametrize('a,b,result', [
    ([1], [1], [1, 1]),
    ({1}, [1], {1}),
    (frozenset({1}), [1, 2], frozenset({1, 2})),
    ((0,), [1, 2], (0, 1, 2)),
    (1, 2, 3),
    ({'a': 1}, {'a': 2}, {'a': 3}),
    ([1], 2, [1, 2]),
    ({1}, 2, {1, 2}),
    (frozenset({1}), 2, frozenset({1, 2})),
    ((1,), 2, (1, 2)),
])
def test_lmerge_values(a, b, result):
    value1 = {'value': a}
    value2 = {'value': b}
    lmerge(value1, value2)
    assert value1['value'] == result, 'Unexpected result'


def test_lmerge_unhashable_add_to_sets():
    with pytest.raises(TypeError) as e:
        lmerge({'a': {1}}, {'a': {}})
    assert 'unhashable' in e.value.args[0]
    with pytest.raises(TypeError) as e:
        lmerge({'a': frozenset({1})}, {'a': {}})
    assert 'unhashable' in e.value.args[0]


def test_lmerge_incompatible_types():
    class A:
        pass

    with pytest.raises(TypeError) as e:
        lmerge({'a': A()}, {'a': object()})

    assert 'a:' in e.value.args[0]


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


def test_extend_set_order():
    store = {'key': ['a', 'b', 'c']}
    extend_set(store, 'key', ['a', 'd', 'e'])
    assert store['key'] == ['a', 'b', 'c', 'd', 'e'], 'Failed to add data in correct order'


def test_extend_set_no_value():
    store = {}
    extend_set(store, 'key', ['a', 'b', 'c'])
    assert store['key'] == ['a', 'b', 'c'], 'Failed to create key'


def test_extend_set_no_change_old():
    target = ['a', 'b', 'c']
    store = {'key': ['a', 'b', 'c']}
    extend_set(store, 'key', ['g', 'g', 'g'])
    assert target == ['a', 'b', 'c'], 'Failed to persist old'


def test_extend_set_de_duplicates_existing():
    store = {'key': ['a', 'a', 'a']}
    extend_set(store, 'key', [])
    assert store['key'] == ['a'], 'Failed to de-duplicate'


def test_extend_set_de_duplicates_new():
    store = {'key': ['a', 'a', 'a']}
    extend_set(store, 'key', ['a', 'a', 'a'])
    assert store['key'] == ['a'], 'Failed to de-duplicate'


def test_transform_adds_value():
    store = {}
    transform_set(store, 'key', int)
    assert 'key' in store, 'Failed to add value'


def test_transform_creates_new_list():
    target = ['1', '2', '3']
    store = {'key': target}
    transform_set(store, 'key', int)
    assert store['key'] is not target


def test_transform_values():
    store = {'key': ['1', '2', '3']}
    transform_set(store, 'key', int)
    assert store['key'] == [1, 2, 3]
