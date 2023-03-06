from pathlib import Path
from typing import Dict

import pytest

from dnsmule.definitions import RRType
from dnsmule.rules import utils, Rule, DynamicRule


class MockRules:
    rtype: RRType
    rule: Rule = object()
    definition: Dict

    def create_rule(self, definition):
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

    utils.load_and_append_rule(
        rules,
        {
            'record': 'TXT',
            'a': 1,
        }
    )

    assert rules.rtype == RRType.TXT, 'Failed to match type'
    assert rules.definition == {'a': 1}, 'Failed to match definition'


def test_rules_utils_load_and_append_dynamic():
    rules = MockRules()

    rules.rule = DynamicRule(code='pass')

    init_marker = []
    rules.rule.init = lambda f: init_marker.append(f)

    utils.load_and_append_rule(
        rules,
        {
            'record': 'TXT',
        }
    )

    assert len(init_marker) == 1, 'Failed to call init'

    m2 = object()
    rules.rule = m2

    init_marker[0]({'record': 'A'})
    assert rules.rtype == RRType.A, 'Failed to call dynamic add'


def test_rules_utils_creates_rules():
    assert utils.load_rules([]) is not None, 'Did not create rules'


def test_rules_utils_takes_name_as_first_key(replace_method):
    definition = {
        'a': None
    }
    replace_method(utils, 'load_and_append_rule', lambda *_, **__: None)
    utils.load_rules([definition])

    assert len(definition) == 1, 'Failed to remove key'
    assert definition['name'] == 'a', 'Failed to modify key to name'


def test_rules_utils_takes_existing_name(replace_method):
    definition = {
        'a': None,
        'name': 'b',
    }
    replace_method(utils, 'load_and_append_rule', lambda *_, **__: None)
    utils.load_rules([definition])

    assert len(definition) == 1, 'Failed to remove key'
    assert definition['name'] == 'b', 'Modified existing name'


def test_rules_utils_pops_only_none(replace_method):
    definition = {
        'a': 'some value'
    }
    replace_method(utils, 'load_and_append_rule', lambda *_, **__: None)
    utils.load_rules([definition])

    assert len(definition) == 2, 'Actually removed not-none key'
    assert definition['name'] == 'a', 'Failed to modify key to name'
    assert definition['a'] == 'some value', 'Did not preserve key'


def test_loading_empty_rules():
    assert utils.load_config(Path(__file__).parent / 'sample_1.yml') is not None, 'Failed to create rules'


def test_loading_existing_rules():
    marker = object()
    rules = utils.load_config(Path(__file__).parent / 'sample_1.yml', rules=marker)
    assert rules is marker, 'Failed to persist rules'
