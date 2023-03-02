import re

import pytest

from dnsmule.definitions import Record, Domain, Data, RRType
from dnsmule.rules.ruletypes import RegexRule


def test_rule_with_pattern_and_patterns():
    rule = RegexRule(
        pattern='a',
        patterns=[
            'b',
            'c'
        ]
    )
    assert rule._patterns == [re.compile(o, flags=re.UNICODE) for o in ('a', 'b', 'c')], 'Did not contain all patterns'


def test_rule_invalid_flag_raises():
    with pytest.raises(ValueError) as e:
        RegexRule(pattern='a', flags=['ööö'])
    assert 'Invalid' in e.value.args[0]


def test_rule_empty_flags_default():
    rule = RegexRule(pattern='a', flags=[])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.UNICODE


def test_rule_flags_reduce():
    rule = RegexRule(pattern='a', flags=[
        'ascii',
        'dotall',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII | re.DOTALL


def test_rule_flags_reduce_same():
    rule = RegexRule(pattern='a', flags=[
        'ascii',
        'ascii',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII


def test_rule_flags_case_insensitive():
    rule = RegexRule(pattern='a', flags=[
        'asCiI',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII


def test_rule_get_attribute_callable():
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


def test_rule_get_attribute_property():
    rule = RegexRule(pattern='test', attribute='value')
    assert rule.get_attribute(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data=Data(
            type=RRType.TXT,
            value='test',
        ),
    )) == 'test', 'Returned the wrong value'
