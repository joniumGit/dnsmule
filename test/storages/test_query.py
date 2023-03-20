from typing import Any

import pytest

from dnsmule import RRType
from dnsmule.storages import Query


def test_any():
    assert Query.ANY is Any, 'Failed to match ANY to a commonly available type'


def test_is_intersect(generate_result):
    result = generate_result()
    result.tag('example')
    result.data['test'] = ['value']

    query = Query(domains=[result.domain], tags=['not found'])
    assert not query(result), 'Matched partial'

    query = Query(domains=['domain'], tags=['example'])
    assert not query(result), 'Matched partial'


def test_transforms_types(generate_result):
    result = generate_result()
    result.type.add(RRType.A)
    result.type.add(RRType.TXT)

    q = Query(types=['A', 'MX', '65530'])
    assert q(result), 'Failed to match types'


@pytest.mark.parametrize('query', [
    Query(data={
        'test_1': [1, 2, 3],
    }),
    Query(data={
        'test_2': '1',
    }),
    Query(data={
        'test_1': 1,
    }),
    Query(data={
        'test_1': Query.ANY,
    }),
    Query(data={
        'test_1': [
            [1, 2, 3],
            [1, 2, ],
            [1, ],
        ],
    }),
])
def test_data_rich_match(generate_result, query):
    result = generate_result()
    result.data['test_1'] = [1, 2, 3]
    result.data['test_2'] = '1,2,3'

    assert query(result), 'Failed to match'


def test_data_no_match(generate_result):
    result = generate_result()
    result.data['test'] = 'value'

    assert not Query(data={})(result), 'Matched on empty'
