import pytest

from dnsmule.plugins import Plugin, Plugins
from dnsmule.plugins.noop import NOOPPlugin


def test_is_abstract():
    with pytest.raises(TypeError):
        Plugin()


def test_takes_kwargs():
    p = NOOPPlugin(a=1)
    assert p.a == 1, 'Did not take kwarg'


def test_skips_underscore_kwargs():
    p = NOOPPlugin(_a=1)
    with pytest.raises(AttributeError):
        _ = p._a


@pytest.mark.parametrize('value', [
    NOOPPlugin.id,
    'plugin.noop',
    NOOPPlugin._id,
    NOOPPlugin,
])
def test_plugins(value):
    plugins = Plugins()
    plugins.add(NOOPPlugin())
    assert plugins.contains(value), 'Failed to contain'
    assert value in plugins, 'Failed to support in'
    assert plugins.get(value) is not None, 'Failed to get plugin'
    assert plugins[value] is not None, 'Failed to get plugin'


def test_iter_plugin_ids():
    plugins = Plugins()
    plugins.add(NOOPPlugin())
    assert [*plugins] == [NOOPPlugin.id], 'Failed to produce ids'
