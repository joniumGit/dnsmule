import pytest

from dnsmule.definitions import Result, RRType, Domain


def test_result_contains_tag():
    r = Result(type=RRType.A, domain=Domain('a'))
    r.tags.add('test')
    assert 'test' in r, 'Result did not contain tag or __contains__ defined wrong'


def test_result_set_get_delegates_to_data():
    r = Result(type=RRType.A, domain=Domain('a'))
    r['test'] = 1
    assert r['test'] == 1, 'Setting item did not persist'
    assert r.data['test'] == 1, 'Setting an item did not set it in data'


def test_result_bool():
    r = Result(type=RRType.A, domain=Domain('a'))
    assert not r, 'Empty result was true'

    r.tags.add('test')
    assert r, 'Result with tags was false'

    r.tags.clear()
    assert not r, 'Clearing tags retained state'

    r['test'] = 1
    assert r, 'Result with data was false'


def test_result_hash():
    s = 'a.example.com'
    d = Domain(s)
    r = Result(type=RRType.A, domain=d)

    assert hash(r) == hash(d), 'Result hash did not equal domain hash'
    assert hash(r) == hash(s), 'Result hash did not equal domain string from'


def test_result_equals():
    s = 'b.example.com'
    d = Domain(s)
    r = Result(type=RRType.A, domain=d)

    assert r == d, 'Result did not equal domain'
    assert r == s, 'Result did not equal domain string from'


def test_result_does_not_equal_other_types():
    r = Result(type=RRType.A, domain=Domain('a'))
    assert 1 != r, 'Result equaled int'


def test_result_type_is_set():
    r = Result(type=RRType.A, domain=Domain('a'))
    assert type(r.tags) == set, 'Result tags was not a set'


def test_result_add_self_noop():
    r = Result(type=RRType.A, domain=Domain('a'))
    r['a'] = ['b']
    r1 = r + r
    assert len(r.type) == 1, 'Result type had unexpected members'
    assert r.data == {'a': ['b']}, 'Result data had additional data'
    assert r1 is r, 'Result instance was not the same'


def test_result_add_other():
    r1 = Result(type=RRType.A, domain=Domain('a'))
    r1['a'] = ['b']

    r2 = Result(type=RRType.TXT, domain=Domain('a'))
    r2.tags.add('test')
    r2['a'] = ['c']

    r = r1 + r2

    assert len(r.type) == 2, 'Result type did not contain all members'
    assert len(r.tags) == 1, 'Result tags did not update'
    assert r.data == {'a': ['b', 'c']}, 'Result data was unexpected format'
    assert r1 is r, 'Result instance was not the left operand'


def test_result_add_different_domain_raises():
    r1 = Result(type=RRType.A, domain=Domain('a'))
    r2 = Result(type=RRType.TXT, domain=Domain('b'))

    with pytest.raises(ValueError):
        r1 + r2


def test_result_add_other_type_raises():
    r1 = Result(type=RRType.A, domain=Domain('a'))

    with pytest.raises(TypeError):
        r1 + ''


def test_result_to_dict():
    r1 = Result(type=RRType.A, domain=Domain('a'))
    r1.type.add(RRType.TXT)
    r1.type.add(RRType.of(65530))
    r1['test'] = [100]
    r1['test2'] = {1}
    r1.tags.add('test-tag')

    assert r1.to_json() == {
        'domain': r1.domain.name,
        'type': [
            'A',
            'TXT',
            65530,
        ],
        'tags': [
            'test-tag',
        ],
        'data': {
            'test': [
                100,
            ],
            'test2': {1}
        }
    }


def test_result_empty_type():
    r = Result(Domain('a'))
    assert r.type == set(), 'Result created with default type'


def test_result_empty_len():
    r = Result(Domain('a'))
    assert len(r) == 0, 'Result had a length'


def test_result_len_iter():
    r = Result(Domain('a'))
    r.tags.add('a')
    r.tags.add('b')
    assert len(r) == 2, 'Result did not have a  length'
    assert {*r} == {'a', 'b'}, 'Result did not have tags from iter'
