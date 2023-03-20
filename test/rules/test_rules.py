import pytest

from dnsmule import Record, Result, RRType, Domain
from dnsmule.rules import Rules, Rule


@pytest.fixture
def rules():
    yield Rules()


def dummy(_: Record) -> Result:
    pass


@pytest.fixture
def dummy_rule():
    yield Rule(f=dummy)


def test_rule_name(rules):
    @rules.add.CNAME
    def my_cool_rule():
        pass

    assert "name='my_cool_rule'" in str(rules[RRType.CNAME].pop())


def test_rule_unknown_type(rules):
    unknown = 65533

    def unknown_type(r: Record):
        return r.result()

    rules.append(unknown, Rule(unknown_type))

    assert "name='unknown_type'" in str(rules[unknown].pop())


def test_iter_returns_items_from_rules(rules):
    rules._rules[RRType.TXT] = []
    assert next(iter(rules)) == (RRType.TXT, []), 'Did not return the expected iteration result'


def test_iter_to_dict(rules, dummy_rule):
    rules._rules[RRType.TXT] = [dummy_rule]

    assert {**rules} == {RRType.TXT: [dummy_rule]}, 'Did not return the expected values'


def test_getitem_returns_items_from_rules(rules, dummy_rule):
    rules._rules[RRType.TXT] = [dummy_rule]

    assert rules[RRType.TXT] == [dummy_rule], 'Did not return from rules'


def test_length_returns_rule_count(rules, dummy_rule):
    rules._rules[RRType.TXT] = [dummy_rule, dummy_rule, dummy_rule]
    rules._rules[RRType.A] = [dummy_rule, dummy_rule, dummy_rule]

    assert len(rules) == 6, 'Did not return rule count'


def test_size_returns_rule_count(rules, dummy_rule):
    rules._rules[RRType.TXT] = [dummy_rule, dummy_rule, dummy_rule]
    rules._rules[RRType.A] = [dummy_rule, dummy_rule, dummy_rule]

    assert rules.size() == 6, 'Did not return rule count'


def test_getitem_returns_items_from_conversion(rules, dummy_rule):
    marker = [dummy_rule]
    rules._rules[RRType.A] = marker

    assert rules[1] is marker, 'Did not convert int'
    assert rules['a'] is marker, 'Did not convert lower string'
    assert rules['A'] is marker, 'Did not convert upper string'


def test_get_types_returns_keys(rules):
    rules._rules[RRType.A] = []
    rules._rules[RRType.TXT] = []

    types = iter(rules.types)
    assert next(types) is RRType.A, 'Unexpected return or order'
    assert next(types) is RRType.TXT, 'Unexpected return or order'


def test_process_error(rules, logger):
    from dnsmule.rules import rules as m
    logger.mock_in_module(m)

    rules.append(RRType.TXT, Rule(f=lambda *_, **__: exec('raise ValueError()')))
    rec = Record(domain=Domain('example.com'), data='', type=RRType.TXT)
    rules.process(rec)

    assert 'error' in logger.result, 'Failed to log error'


def test_process_normal_rule(rules):
    class MockRule(Rule):
        called = set()

        def __call__(self, *args, **kwargs):
            self.called.add('__call__')
            return None

        def __getattr__(self, item):
            self.called.add(item)

        def __await__(self):
            assert False, 'Should not be called'

    rules.append(RRType.MX, MockRule())

    rules.process(Record(domain=Domain('example.com'), data='', type=RRType.MX))

    assert MockRule.called == {'__call__'}, 'Not all or too many methods were called'


def test_contains_dunder():
    r = Rules()
    assert RRType.A not in r, 'Contained data even though empty'


def test_get_defaults():
    r = Rules()
    assert RRType.A not in r, 'Contained data even though empty'
    assert r[RRType.A] == [], 'Did not default'


def test_contains():
    r = Rules()
    r._rules[RRType.A] = [Rule(f=dummy, name='a')]

    assert r.contains('A', 'a'), 'Failed to have rule for str'
    assert r.contains(1, 'a'), 'Failed to have rule for int'
    assert r.contains(RRType.A, 'a'), 'Failed to have rule for RRType'
    assert r.contains('1', 'a'), 'Failed to have rule for RRType'


def test_process_normal_rule_results_appended(rules):
    class MockRule(Rule):

        def __call__(self, rec):
            r = Result(rec.domain)
            r.data['hello'] = ['world']
            return r

    rules.append(RRType.MX, MockRule())

    record = Record(domain=Domain('example.com'), data='', type=RRType.MX)
    result = record.result

    rules.process(record)

    assert result is record.result, 'Did not get expected result'
    assert result.data['hello'] == ['world'], 'Did not append new data'


def test_rules_add_rule_twice_ok_different_name(rules):
    rules.append('A', Rule(dummy))
    rules.append('A', Rule(dummy, name='test_2'))
    assert len(rules['A']) == 2, 'Failed to add to the same place'


def test_rules_add_rule_twice_same_name(rules):
    rules.append('A', Rule(dummy))
    with pytest.raises(ValueError):
        rules.append('A', Rule(dummy))
