import pytest

from dnsmule.definitions import Domain, Result, RRType, Record
from dnsmule.storage import ResultMapper, RecordMapper, RRTypeMapper


def test_mappers_result_to_dict():
    r1 = Result(type=RRType.A, domain=Domain('a'))
    r1.type.add(RRType.TXT)
    r1.type.add(RRType.of(65530))
    r1['test'] = [100]
    r1['test2'] = {1}
    r1.tags.add('test-tag')

    assert ResultMapper.to_json(r1) == {
        'domain': r1.domain,
        'type': [
            'A',
            'TXT',
            '65530',
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


def test_mappers_result_from_dict():
    r1 = ResultMapper.from_json(
        {
            'domain': 'example.com',
            'type': [
                'CNAME',
                '65520',
            ],
            'tags': [
                'test-tag',
                'test-tag-1',
            ],
            'data': {
                'test': [
                    100,
                ],
                'test2': {2}
            }
        }
    )
    r2 = Result('example.com', RRType.CNAME)
    r2.type.add(RRType.of(65520))
    r2.tags.update(('test-tag', 'test-tag-1'))
    r2.data.update({
        'test': [
            100,
        ],
        'test2': {2}
    })
    assert r1 == r2, 'Failed to produce correct result'


def test_mappers_record_has_result():
    r = Record('example.com', RRType.CNAME, 'value')
    assert 'result' not in RecordMapper.to_json(r), 'Contained result'
    r.result()
    assert 'result' not in RecordMapper.to_json(r), 'Contained empty result'
    r.identify('a')
    assert 'result' in RecordMapper.to_json(r), 'Failed to contain non-empty result'


def test_mappers_record_deserializes_result():
    r = Record('example.com', RRType.CNAME, 'value')
    r.identify('a')

    r1 = RecordMapper.from_json(RecordMapper.to_json(r))
    assert r1 == r, 'Failed equals'
    assert r1.result() == r.result(), 'Failed to deserialize result'


def test_mappers_record_deserializes_no_result():
    r = Record('example.com', RRType.CNAME, 'value')
    assert not r.result(), 'Had a non empty result'

    data = RecordMapper.to_json(r)
    assert 'result' not in data, 'Serialized empty result'

    r1 = RecordMapper.from_json(data)
    assert not r1.result(), 'Has a non-empty result after deserialization'


def test_mappers_rrtype_is_str():
    assert type(RRTypeMapper.to_json(RRType.A)) == str, 'Not the right type'


def test_mappers_rrtype_value():
    assert type(RRTypeMapper.to_json(65520)) == str, 'Not the right type'
    assert RRTypeMapper.from_json('65520') == RRType.from_any('65520'), 'Not the right value'
    assert RRTypeMapper.from_json('1') == RRType.A, 'Not the right value'


def test_mappers_throws_on_bad_value():
    with pytest.raises(KeyError):
        ResultMapper.from_json({
            'name': 'a'
        })
