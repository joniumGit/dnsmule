import re

import pytest

from dnsmule.definitions import Record, Domain, Data, RRType
from dnsmule.rules.ruletypes import RegexRule


def test_regex_rule_with_pattern_and_patterns():
    rule = RegexRule(
        pattern='a',
        patterns=[
            'b',
            'c'
        ]
    )
    assert rule._patterns == [re.compile(o, flags=re.UNICODE) for o in ('a', 'b', 'c')], 'Did not contain all patterns'


def test_regex_rule_invalid_flag_raises():
    with pytest.raises(ValueError) as e:
        RegexRule(pattern='a', flags=['ööö'])
    assert 'Invalid' in e.value.args[0]


def test_regex_rule_empty_flags_default():
    rule = RegexRule(pattern='a', flags=[])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.UNICODE


def test_regex_rule_flags_reduce():
    rule = RegexRule(pattern='a', flags=[
        'ascii',
        'dotall',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII | re.DOTALL


def test_regex_rule_flags_reduce_same():
    rule = RegexRule(pattern='a', flags=[
        'ascii',
        'ascii',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII


def test_regex_rule_flags_case_insensitive():
    rule = RegexRule(pattern='a', flags=[
        'asCiI',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII


def test_regex_rule_get_attribute_callable():
    rule = RegexRule(pattern='test', attribute='__str__')
    data = Data(
        type=RRType.TXT,
        value='test',
    )
    assert rule.get_attribute(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=data,
    )) == str(data), 'Returned the wrong attribute'


def test_regex_rule_get_attribute_property():
    rule = RegexRule(pattern='test', attribute='value')
    assert rule.get_attribute(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='test',
        ),
    )) == 'test', 'Returned the wrong value'


def test_regex_rule_empty_patterns():
    r = RegexRule(pattern=None, patterns=[])
    assert r._patterns == [], 'Patterns somehow compiled with empty input'


def test_regex_rule_match_no_id_no_group():
    rule = RegexRule(pattern='test', attribute='value', name='a')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='test',
        ),
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::A::UNKNOWN', 'Did not work without id or group'


def test_regex_rule_match_no_id_group_int():
    rule = RegexRule(pattern='(test)', attribute='value', name='a', group=1)
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='test',
        ),
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::A::TEST', 'Did not use group'


def test_regex_rule_match_no_id_group_str():
    rule = RegexRule(pattern='(?P<a>test)', attribute='value', name='a', group='a')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='test',
        ),
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::A::TEST', 'Did not user group'


def test_regex_rule_match_id_no_group():
    rule = RegexRule(pattern='test', attribute='value', name='GGG', identification='a')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='test',
        ),
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::GGG::A', 'Did not use identification name'


def test_regex_rule_no_match():
    rule = RegexRule(pattern='^test$', attribute='value')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='testadwadaw',
        ),
    ))
    assert res is None, 'Mathced invalid value'
