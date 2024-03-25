from dnsmule import ContainsRule, Record, Result, RRType, Domain


def test_contains_rule_appends_tag_to_result_on_matching():
    rule = ContainsRule(identities=[{
        'value': 'a.example',
        'name': 'example',
        'type': 'CDN'
    }])

    record = Record(
        name=Domain('example.com'),
        type=RRType.CNAME,
        data='a.example.com',
    )

    result = Result(
        name=Domain('example.com'),
    )

    rule(record, result)

    assert 'DNS::CIDER::CDN::EXAMPLE' in result.tags


def test_contains_rule_does_nothing_on_not_matching():
    rule = ContainsRule(identities=[{
        'value': 'a.example',
        'name': 'example',
        'type': 'CDN'
    }])

    record = Record(
        name=Domain('example.com'),
        type=RRType.CNAME,
        data='b.example.com',
    )

    result = Result(
        name=Domain('example.com'),
    )

    rule(record, result)

    assert not result.tags
