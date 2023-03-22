from typing import Any

from dnsmule import RRType
from dnsmule.storages import Query


def test_any():
    assert Query.ANY is Any, 'Failed to match ANY to a commonly available type'


def test_is_intersect(generate_result):
    result = generate_result()
    result.tag('example')
    result.data['test'] = ['value']

    query = Query(domains=[result.domain], tags='not found')
    assert not query(result), 'Matched partial'

    query = Query(domains=['domain'], tags='example')
    assert not query(result), 'Matched partial'


def test_transforms_types(generate_result):
    result = generate_result()
    result.type.add(RRType.A)
    result.type.add(RRType.TXT)

    q = Query(types=['A', 'MX', '65530'])
    assert q(result), 'Failed to match types'


def test_tags_partial_match(generate_result):
    result = generate_result()
    result.tag('IP::PTR::AAAA')

    assert Query(tags='IP::PTR')(result), 'Failed partial tag match'


def test_domain_partial_match(generate_result):
    result = generate_result()
    result.domain = 'a.a.com'

    assert Query(domains=['*.a.com'])(result), 'Failed star domain match'


def test_domain_match(generate_result):
    result = generate_result()
    result.domain = 'a.com'

    result1 = generate_result()
    result1.domain = 'a.a.com'

    assert Query(domains=['a.com'])(result), 'Failed domain match'
    assert not Query(domains=['a.com'])(result1), 'Matched subdomain without star'


def test_types_match(generate_result):
    result = generate_result()
    result.type.add(RRType.A)
    result.type.add(RRType.TXT)

    assert Query(types=['CNAME', 'MX', 'A'])(result), 'Failed type match'


def test_types_no_match(generate_result):
    result = generate_result()
    result.type.add(RRType.TXT)

    assert not Query(types=['CNAME', 'MX', 'A'])(result), 'Produced match without valid value'


def test_tags_regex(generate_result):
    result = generate_result()
    result.type.add(RRType.TXT)
    result.tag('IP::PTR::CUSTOM_RULE_NAME::PROVIDER')

    assert Query(tags='^IP::PTR::.*?::PROVIDER')(result), 'Failed to match regex'


def test_data_regex(generate_result):
    result = generate_result()
    result.type.add(RRType.TXT)
    result.data['key'] = 'value'

    assert Query(data='\'key\':\\s*?.value')(result), 'Failed to match regex'
