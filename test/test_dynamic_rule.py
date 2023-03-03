import pytest

from dnsmule.rules.ruletypes import DynamicRule


def test_dynamic_rule_invalid_code():
    with pytest.raises(SyntaxError):
        DynamicRule(code='dwadawd awd wa')


def test_dynamic_rule_no_code():
    with pytest.raises(ValueError):
        DynamicRule(code=None)


def test_dynamic_rule_without_process_or_init():
    r = DynamicRule(code='a = 10')

    r.init(lambda *_: DynamicRule())

    assert r.globals['a'] == 10, 'Globals not updated on init'


def test_dynamic_rule_callback_called(code='add_rule("a", "b", "c")'):
    r = DynamicRule(code=code)
    called = [False]

    def callback(name, config):
        called[0] = True
        assert name == 'c', 'Name did not match'
        assert config == {
            'record': 'a',
            'type': 'b',
            'priority': 0,
        }, 'Config did not match'
        return DynamicRule(code='a = 1')

    r.init(callback)

    assert called[0], 'Callback not called'


def test_dynamic_rule_callback_called_on_init():
    test_dynamic_rule_callback_called(code='def init():\n    add_rule("a", "b", "c")')


def test_dynamic_rule_without_process_returns_none():
    r = DynamicRule(code='a = 1')
    assert r(1) is None, 'Calling rule produces a result without process'


def test_dynamic_rule_callback_called_on_process():
    r = DynamicRule(code='def process(record):\n    assert record == 1, "Not called with right args"\n    return 2')
    assert r(1) is None, 'Process worked without init'
    r.init(None)
    assert r(1) == 2, 'Process method did not get called'


def test_dynamic_rule_available_names():
    DynamicRule(
        code='a = int("10");'
             ' import math;'
             ' b = RRType.TXT;'
             ' c = Record(domain="a", data="b", type=RRType.A);'
             ' d = add_rule;'
             ' e = Result(type=RRType.AAAA, domain=None)'
    ).init(None)


def test_dynamic_rule_globals_persist():
    r = DynamicRule(
        code='a = 1\n'
             'def init():\n'
             '    global a\n'
             '    assert a == 1\n'
             '    a = 10\n'
             'def process(record):\n'
             '    global a\n'
             '    assert a == 10\n'
             '    a = 20\n'
    )
    r.init(None)
    r(1)
    assert r.globals['a'] == 20, 'Globals did not persist'
