from typing import Dict

import pytest

from dnsmule.definitions import RRType
from dnsmule.loader import load_rules, load_and_append_rule
from dnsmule.rules import Rule, DynamicRule, Rules


class MockRules(Rules):
    rtype: RRType
    rule: Rule = object()
    definition: Dict

    def create_rule(self, type_name, definition):
        self.definition = definition
        return self.rule

    def add_rule(self, rtype, rule):
        self.rtype = rtype
        assert rule is self.rule, 'Did not get marker object'


@pytest.fixture
def replace_method():
    store = []

    def replace(o, name, method):
        old = getattr(o, name)
        store.append(lambda: setattr(o, name, old))
        setattr(o, name, method)

    yield replace

    for f in store:
        f()


def test_rules_utils_load_and_append():
    rules = MockRules()

    load_and_append_rule(
        rules,
        RRType.TXT,
        'type',
        {
            'a': 1,
        },
    )

    assert rules.rtype == RRType.TXT, 'Failed to match type'
    assert rules.definition == {'a': 1}, 'Failed to match definition'


def test_rules_utils_load_and_append_dynamic():
    rules = MockRules()

    rules.rule = DynamicRule(code='pass')

    init_marker = []
    rules.rule.init = lambda f: init_marker.append(f)

    load_and_append_rule(
        rules,
        RRType.TXT,
        'dns.dynamic',
        {

        },
    )

    assert len(init_marker) == 1, 'Failed to call init'

    m2 = object()
    rules.rule = m2

    init_marker[0](
        RRType.A,
        'dns.dynamic',
        {

        },
    )
    assert rules.rtype == RRType.A, 'Failed to call dynamic add'


def test_rules_utils_creates_rules():
    assert load_rules([]) is not None, 'Did not create rules'


def test_rules_utils_leaves_name(replace_method):
    definition = {
        'name': 'a',
        'record': RRType.A,
        'type': 'dns.regex',
        'config': {
            'name': 'abcd'
        }
    }
    rules = load_rules([definition])
    assert rules[RRType.A][0].name == 'abcd', 'Name was changed from one in config'


def test_rules_utils_takes_name(replace_method):
    definition = {
        'name': 'a',
        'record': RRType.A,
        'type': 'dns.regex',
        'config': {
        }
    }
    rules = load_rules([definition])
    assert rules[RRType.A][0].name == 'a', 'Name was not rule name'
