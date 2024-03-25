import pytest

from dnsmule.rules import DynamicRule


def test_invalid_code():
    with pytest.raises(SyntaxError):
        DynamicRule(code='dwadawd awd wa')


def test_no_code():
    with pytest.raises(TypeError):
        DynamicRule(code=None)


def test_without_process_or_init():
    r = DynamicRule(code='a = 10')
    with r:
        assert r._globals['a'] == 10, 'Globals not updated on init'


def test_without_process_returns_none(generate_record):
    r = DynamicRule(code='a = 1')
    with r:
        assert r(generate_record()) is None, 'Calling rule produces a result without process'


def test_available_names():
    with DynamicRule(
            code='a = int("10");'
                 ' import math;'
                 ' b = RRType.TXT;'
                 ' c = Record(name=Domain("a"), data="b", type=RRType.A);'
                 ' e = Result(types=[RRType.AAAA], name=None);'
    ):
        pass


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
    with r:
        r(generate_record())
        assert r._globals['a'] == 20, 'Globals did not persist'


def test_config_available():
    r = DynamicRule(
        my_config_values={
            'a': 123,
            'b': 10,
        },
        code='pass',
    )
    with r:
        assert 'Config' in r._globals, 'Failed to have Config global'
        assert r._globals['Config'].my_config_values is not None, 'Failed to contain Config namespace'
