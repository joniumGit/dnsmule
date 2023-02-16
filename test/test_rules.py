from typing import cast

import pytest

from dnsmule.rules.rules import Rule, RULES, rule, Type, add_rule, Result, Record


@pytest.fixture(autouse=True)
def clear_rules():
    RULES.clear()
    yield
    RULES.clear()


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


def test_rules_rule_name():
    @rule.CNAME
    def my_cool_rule():
        pass

    assert 'name=my_cool_rule' in str(RULES[Type.CNAME].pop())


def test_rules_rule_unknown_type():
    unknown = cast(Type, 13213213123)

    def unknown_type():
        pass

    add_rule(unknown, 0)(unknown_type)

    assert 'name=unknown_type' in str(RULES[unknown].pop())
