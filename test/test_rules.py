from typing import cast

import pytest

from dnsmule.rules.rules import Rule, Type, Result, Record, Rules


@pytest.fixture
def rules():
    yield Rules()


def dummy(_: Record) -> Result:
    pass


def test_rules_rule_ordering():
    r0 = Rule(dummy, 0)
    r1 = Rule(dummy, 1)
    r2 = Rule(dummy, 2)

    data = [r2, r0, r1]
    data.sort()

    # priority is inverted
    assert data == [r2, r1, r0]


def test_rules_rule_ordering_with_changes():
    r0 = Rule(dummy, 0)
    r1 = Rule(dummy, 1)

    data = [r0, r1]
    data.sort()

    # priority is inverted
    assert data == [r1, r0]

    r1.priority = -1
    data.sort()

    # assert changes order
    assert data == [r0, r1]


def test_rules_rule_name(rules):
    @rules.CNAME
    def my_cool_rule():
        pass

    assert 'f=my_cool_rule' in str(rules[Type.CNAME].pop())


def test_rules_rule_unknown_type(rules):
    unknown = cast(Type, 13213213123)

    def unknown_type():
        pass

    rules.add_rule(unknown, 0)(unknown_type)

    assert 'f=unknown_type' in str(rules[unknown].pop())


def test_rules_factory_operation(rules):
    @rules.register('test')
    def my_cool_rule(name: str):
        assert name == 'hello_world'

    rules.load_config([
        {
            'type': 'test',
            'record': 'TXT',
            'name': 'hello_world',
        }  # TODO: FIx this name thingy to be better from yaml and add it to rule
    ])

    assert rules[Type.TXT].pop().f is None
