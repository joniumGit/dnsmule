import pytest

from dnsmule import RegexRule, Record, RRType, Domain


@pytest.fixture
def record():
    yield Record(
        name=Domain('test'),
        type=RRType.A,
        data='__sample__'
    )


def test_regex_rule_no_match(record, result):
    rule = RegexRule(name='test', patterns=[{
        'regex': 'nomatch',
        'label': 'match',
    }])

    rule(record, result)

    assert not result.tags


def test_regex_rule_simple_label_match(record, result):
    rule = RegexRule(name='test', patterns=[{
        'regex': 'sample',
        'label': 'match',
    }])

    rule(record, result)

    assert 'DNS::REGEX::TEST::MATCH' in result.tags


def test_regex_rule_simple_group_match(record, result):
    rule = RegexRule(name='test', patterns=[{
        'regex': '(sample)',
        'group': 1,
    }])

    rule(record, result)

    assert 'DNS::REGEX::TEST::SAMPLE' in result.tags


def test_regex_rule_simple_string_group_match(record, result):
    rule = RegexRule(name='test', patterns=[{
        'regex': '(?P<id>sample)',
        'group': 'id',
    }])

    rule(record, result)

    assert 'DNS::REGEX::TEST::SAMPLE' in result.tags
