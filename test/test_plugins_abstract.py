import pytest

from dnsmule.plugins import Plugin
from dnsmule.plugins.noop import NOOPPlugin


def test_plugins_is_abstract():
    with pytest.raises(TypeError):
        Plugin()


def test_plugins_takes_kwargs():
    p = NOOPPlugin(a=1)
    assert p.a == 1, 'Did not take kwarg'


def test_plugins_skips_underscore_kwargs():
    p = NOOPPlugin(_a=1)
    with pytest.raises(AttributeError):
        p._a


def test_plugins_noop_noop():
    p = NOOPPlugin()
    p.register(None)
