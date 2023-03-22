from typing import Any

import pytest

from dnsmule.rules.ruletypes import DynamicRule


def dummy(*_: Any):
    pass


def test_invalid_code():
    with pytest.raises(SyntaxError):
        DynamicRule(code='dwadawd awd wa')


def test_no_code():
    with pytest.raises(ValueError):
        DynamicRule(code=None)


def test_without_process_or_init():
    r = DynamicRule(code='a = 10')

    r.init(dummy)

    assert r.globals['a'] == 10, 'Globals not updated on init'


def test_callback_called(code='add_rule("a", "b", "c")'):
    r = DynamicRule(code=code)
    called = [False]

    def callback(record: Any, rtype: Any, config: Any):
        called[0] = True
        assert record == 'a', 'Record type did not match'
        assert rtype == 'b', 'Rule type did not match'
        assert config == {
            'name': 'c',
            'priority': 0,
        }, 'Config did not match'

    r.init(callback)

    assert called[0], 'Callback not called'


def test_callback_called_on_init():
    test_callback_called(code='def init():\n    add_rule("a", "b", "c")')


def test_without_process_returns_none(generate_record):
    r = DynamicRule(code='a = 1')
    assert r(generate_record()) is None, 'Calling rule produces a result without process'


def test_callback_called_on_process(generate_record):
    record = generate_record()
    r = DynamicRule(
        code=f'def process(record):\n'
             f'    assert record.domain == "{record.domain}", "Not called with right args"\n'
             f'    return 2'
    )
    assert r(record) is None, 'Process worked without init'
    r.init(dummy)
    assert r(record) == 2, 'Process method did not get called'


def test_available_names():
    DynamicRule(
        code='a = int("10");'
             ' import math;'
             ' b = RRType.TXT;'
             ' c = Record(domain=Domain("a"), data="b", type=RRType.A);'
             ' d = add_rule;'
             ' e = Result(initial_type=RRType.AAAA, domain=None);'
             ' f = Tag("a");'
    ).init(dummy)


def test_globals_persist(generate_record):
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
    r.init(dummy)
    r(generate_record())
    assert r.globals['a'] == 20, 'Globals did not persist'


def test_config_available():
    r = DynamicRule(
        my_config_values={
            'a': 123,
            'b': 10,
        },
        code='pass',
    )
    assert 'Config' in r.globals, 'Failed to have Config global'
    assert r.globals['Config'].my_config_values is not None, 'Failed to contain Config namespace'
