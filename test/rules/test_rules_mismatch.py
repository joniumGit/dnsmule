from dnsmule import Result, MismatchRule, Domain, RRType


def test_mismatch_adds_tags_and_data_to_scan_result(record):
    result = Result(
        name=Domain('alternative.com'),
        types=[RRType.TXT],
        tags=[],
    )

    rule = MismatchRule()
    rule(record, result)

    assert 'DNS::MISMATCH' in result.tags
    assert result.data['aliases'] == ['example.com']


def test_mismatch_does_nothing_on_same_domain(record, result):
    rule = MismatchRule()
    rule(record, result)

    assert not result.tags, 'Rule was activated even though domains were the same'
    assert 'aliases' not in result.data, 'Alias was added on same domains'
