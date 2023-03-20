from dnsmule import Record, RRType, Domain, Result


def test_record_not_equals_other_types():
    r = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    assert r != 1, 'Record equaled int'
    assert r != 'a', 'Record equaled string'


def test_record_create_equals():
    r1 = Record(domain='example.com', type=RRType.A, data='data')
    r2 = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    assert r1 == r2, 'Records were not equal'


def test_record_has_result():
    r = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    assert r._result is not None, 'Record was not created with a result'
    assert r.result is not None, 'Result did not exist'
    assert r.result is r._result, 'Result was a different object'


def test_record_not_equals_different_type():
    r1 = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    r2 = Record(domain=Domain('example.com'), type=RRType.AAAA, data='data')
    assert r1 != r2, 'Different record types were equal'


def test_record_hash_is_tuple_domain_type():
    r = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    assert hash(r) == hash((r.domain, r.type)), 'Hash result was unexpected'


def test_record_identify():
    r = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    r.tag('a')
    assert next(iter(r.result.tags)) == 'a'


def test_record_assign_result_adds():
    r = Record(domain=Domain('example.com'), type=RRType.A, data='data')
    r.tag('a')
    previous = r.result
    r.result = Result(domain=Domain('example.com'))
    assert r.result is previous, 'Failed to persist result instance'


def test_record_text_property_default():
    r = Record(domain=Domain('example.com'), type=RRType.A, data=object())
    assert r.text == str(r.data), 'Failed default impl'
