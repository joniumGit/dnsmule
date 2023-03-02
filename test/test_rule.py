from typing import cast

import pytest

from dnsmule.definitions import Record, Result
from dnsmule.rules import Rule


def dummy(_: Record) -> Result:
    pass


class RuleFunc:

    def __call__(self, r: Record) -> Result:
        pass

    def __str__(self):
        return 'RuleFunc()'

    def __repr__(self):
        return self.__str__()


def test_rule_ordering():
    r0 = Rule(dummy, priority=0)
    r1 = Rule(dummy, priority=1)
    r2 = Rule(dummy, priority=2)

    data = [r2, r0, r1]
    data.sort()

    # priority is inverted
    assert data == [r2, r1, r0], 'Rules were not sorted correctly'


def test_rule_ordering_with_changes():
    r0 = Rule(dummy, priority=0)
    r1 = Rule(dummy, priority=1)

    data = [r0, r1]
    data.sort()

    # priority is inverted
    assert data == [r1, r0], 'Rules were sorted incorrectly'

    r1.priority = -1
    data.sort()

    # assert changes order
    assert data == [r0, r1], 'Rule ordering did not change'


def test_rule_equals_name():
    r0 = Rule(dummy)
    r1 = Rule(lambda o: o.result(), name='dummy')
    assert r0 == r1, 'Rules equals did not match names'


def test_rule_none_name_is_not_none():
    r1 = Rule(lambda o: o.result(), name=None)
    assert r1.name is not None, 'Name was none'


def test_rule_f_not_callable_raises():
    with pytest.raises(ValueError) as e:
        Rule(cast(RuleFunc, 'adwdaw'), name='test')
    assert 'callable' in e.value.args[0], 'Raised unexpected value error'


def test_rule_f_none_raises():
    with pytest.raises(ValueError) as e:
        Rule(None, name='test')
    assert 'None' in e.value.args[0], 'Raised unexpected value error'


def test_rule_f_none_subclass_with_call_ok():
    class A(Rule):
        def __call__(self, *args, **kwargs):
            pass

    r = A(None, name='test')

    assert r.f == r.__call__, 'Method was not the expected __call__ method'


def test_rule_f_none_subclass_without_call_raises():
    class B(Rule):
        pass

    with pytest.raises(ValueError) as e:
        B(None, name='test')

    assert 'None' in e.value.args[0], 'Subclass without __call__ did not raise on f=None'


def test_rule_call_recursion_prevention():
    r = Rule(lambda: None, name='test')
    r.f = r.__call__
    with pytest.raises(RecursionError) as e:
        r('a')
    assert 'detected' in e.value.args[0], 'Raised recursion error from somewhere else'


def test_rule_repr_eq_str():
    r = Rule(lambda: None, name='test', a=1)
    assert repr(r) == str(r), 'Representations were not equal'


def test_rule_repr_eval():
    r = Rule(RuleFunc(), name='test', a=1, b=2, c='ggg')
    r1 = eval(repr(r))
    assert r1 == r, 'Eval did not produce equal rule'
    assert r1.a == r.a, 'Missing kwarg'
    assert r1.b == r.b, 'Missing kwarg'
    assert r1.c == r.c, 'Missing kwarg'
    assert isinstance(r1.f, RuleFunc), 'Rule had an unexpected f'


def test_rule_call_ok():
    def func(value):
        assert value == 'test-value'
        return value + '-1'

    r = Rule(func, name='test')

    assert r('test-value') == 'test-value-1', 'Call failed'


def test_rule_equals_by_name():
    r1 = Rule(dummy, name='test')
    r2 = Rule(RuleFunc(), name='test')
    assert r1 == 'test', 'Rule did not equal string same as name'
    assert r1 == r2, 'Rule did not equal Rule with the same name'


def test_rule_hash_equals_name_hash():
    r1 = Rule(dummy, name='test')
    assert hash(r1) == hash(r1.name), 'Unexpected hash value'
