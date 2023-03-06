import pytest

from dnsmule.definitions import Record, RRType, Domain, Data


def test_record_not_equals_other_types():
    r = Record(domain='example.com', type=RRType.A, data='data')
    assert 1 != r, 'Record equaled int'
    assert 'a' != r, 'Record equaled string'


def test_record_create_equals():
    r1 = Record(domain='example.com', type=RRType.A, data='data')
    r2 = Record(domain=Domain(name='example.com'), type=RRType.A, data='data')
    r3 = Record(domain=Domain(name='example.com'), type=RRType.A, data=Data(type=RRType.A, value='data'))
    assert r1 == r2 == r3, 'Records were not equal'


def test_record_data_type_mismatch():
    with pytest.raises(ValueError):
        Record(domain='example.com', type=RRType.A, data=Data(type=RRType.TXT, value='test'))


def test_record_has_result():
    r = Record(domain='example.com', type=RRType.A, data='data')
    assert r._result is None, 'Record was created with a result'
    assert r.result() is not None, 'Result did not exist'
    assert r.result() is r._result, 'Result was a different object'


def test_record_identify_returns_same_result():
    r = Record(domain='example.com', type=RRType.A, data='data')
    res1 = r.result()
    res2 = r.identify('a')
    assert res1 is res2, 'Results were different objects'
    assert 'a' in res1.tags, 'Results modifications did not show'


def test_record_not_equals_different_type():
    r1 = Record(domain='example.com', type=RRType.A, data='data')
    r2 = Record(domain='example.com', type=RRType.AAAA, data='data')
    assert r1 != r2, 'Different record types were equal'


def test_record_hash_is_tuple_domain_type():
    r = Record(domain='example.com', type=RRType.A, data='data')
    assert hash(r) == hash((r.domain, r.type)), 'Hash result was unexpected'


def test_record_identify():
    r = Record(domain='example.com', type=RRType.A, data='data')
    res = r.identify('a')
    assert next(iter(res.tags)) == 'a'


def test_record_getitem_contains_setitem():
    r = Record(domain='example.com', type=RRType.A, data='data')
    r['a'] = 'abcd'
    assert 'a' in r, 'Failed contains'
    assert r['a'] == 'abcd', 'Failed item get'
