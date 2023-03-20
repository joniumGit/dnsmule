import re

import pytest

from dnsmule.definitions import Record, Domain, RRType
from dnsmule.rules.ruletypes import RegexRule


def test_with_pattern_and_patterns():
    rule = RegexRule(
        pattern='a',
        patterns=[
            'b',
            'c'
        ]
    )
    assert rule._patterns == [re.compile(o, flags=re.UNICODE) for o in ('a', 'b', 'c')], 'Did not contain all patterns'


def test_invalid_flag_raises():
    with pytest.raises(ValueError) as e:
        RegexRule(pattern='a', flags=['ööö'])
    assert 'Invalid' in e.value.args[0]


def test_empty_flags_default():
    rule = RegexRule(pattern='a', flags=[])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.UNICODE


def test_flags_reduce():
    rule = RegexRule(pattern='a', flags=[
        'ascii',
        'dotall',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII | re.DOTALL


def test_flags_reduce_same():
    rule = RegexRule(pattern='a', flags=[
        'ascii',
        'ascii',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII


def test_flags_case_insensitive():
    rule = RegexRule(pattern='a', flags=[
        'asCiI',
    ])
    p: re.Pattern = rule._patterns[0]
    assert p.flags == re.ASCII


def test_empty_patterns():
    r = RegexRule(pattern=None, patterns=[])
    assert r._patterns == [], 'Patterns somehow compiled with empty input'


def test_match_no_id_no_group():
    rule = RegexRule(pattern='test', attribute='value', name='a')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data='test',
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::A::UNKNOWN', 'Did not work without id or group'


def test_match_no_id_group_int():
    rule = RegexRule(pattern='(test)', attribute='value', name='a', group=1)
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data='test',
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::A::TEST', 'Did not use group'


def test_match_no_id_group_str():
    rule = RegexRule(pattern='(?P<a>test)', attribute='value', name='a', group='a')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data='test',
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::A::TEST', 'Did not user group'


def test_match_id_no_group():
    rule = RegexRule(pattern='test', attribute='value', name='GGG', identification='a')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data='test',
    ))
    assert next(iter(res.tags)) == 'DNS::REGEX::GGG::A', 'Did not use identification name'


def test_no_match():
    rule = RegexRule(pattern='^test$', attribute='value')
    res = rule(Record(
        domain=Domain(''),
        type=RRType.TXT,
        data='testadwadaw',
    ))
    assert not res, 'Mathced invalid value'
