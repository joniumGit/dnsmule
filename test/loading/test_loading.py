from pathlib import Path

import pytest

from dnsmule import DNSMule, Rules, Plugins
from dnsmule.backends.noop import NOOPBackend
from dnsmule.loader import import_class, ConfigLoader
from dnsmule.plugins.noop import NOOPPlugin
from dnsmule.storages.dictstorage import DictStorage


@pytest.fixture
def sample_1():
    yield DNSMule.load(Path(__file__).parent / 'sample_1.yml')


@pytest.fixture
def sample_2():
    yield DNSMule.load(Path(__file__).parent / 'sample_2.yml')


@pytest.fixture
def loader_test_init():
    mule = DNSMule.make()
    mule.rules = None
    mule.plugins = None
    mule.backend = None
    mule.storage = None
    yield mule, ConfigLoader(mule)


def test_empty_rules(sample_1):
    assert sample_1.rules is not None, 'Failed to create rules'


def test_empty_plugins(sample_1):
    assert sample_1.plugins is not None, 'Failed to create plugins'


def test_backend(sample_1):
    assert type(sample_1.backend) == NOOPBackend, 'Failed relative import'


def test_plugin(sample_1):
    assert sample_1.plugins.get(NOOPPlugin), 'Failed plugin import'


def test_storage(sample_1):
    assert type(sample_1.storage) == DictStorage, 'Failed storage import'


def test_backend_defaults(sample_2):
    assert type(sample_2.backend) == NOOPBackend


def test_storage_defaults(sample_2):
    assert type(sample_2.storage) == DictStorage


@pytest.mark.parametrize('attribute', [
    'rules',
    'plugins',
    'backend',
    'storage',
])
def test_empty_definitions(loader_test_init, attribute):
    mule, loader = loader_test_init
    for definition in [
        {attribute: None},
        {attribute: []},
        {},
    ]:
        loader.config = definition
        getattr(loader, f'set_{attribute}', getattr(loader, f'append_{attribute}', None))()
        assert getattr(mule, attribute) is None, f'Touched {attribute}'


def test_backends_importing_from_module(loader_test_init):
    mule, loader = loader_test_init
    loader.config = {
        'backend': {
            'name': 'dnsmule.backends.noop.NOOPBackend'
        }
    }
    loader.set_backend()
    assert type(mule.backend) == NOOPBackend, 'Failed to import from anywhere'


def test_backends_importing_fails(loader_test_init):
    _, loader = loader_test_init
    loader.config = {
        'backend': {
            'name': 'dawdwa.dwadwadawdwadaw.awdwdawdawdaw.NOTEXISTING'
        }
    }
    with pytest.raises(ImportError):
        loader.set_backend()


def test_backends_importing_fails_attrib(loader_test_init):
    _, loader = loader_test_init
    loader.config = {
        'backend': {
            'name': 'dnsmule.backends.noop.NOTEXISTING'
        }
    }
    with pytest.raises(ImportError):
        loader.set_backend()


def test_backends_importing_fails_attrib_relative(loader_test_init):
    _, loader = loader_test_init
    loader.config = {
        'backend': {
            'name': 'noop.NOTEXISTING'
        }
    }
    with pytest.raises(ImportError):
        loader.set_backend()


def test_import_class_mismatch():
    with pytest.raises(ImportError):
        import_class('dnsmule.plugins.noop.NOOPPlugin', NOOPBackend, relative=False)


def test_bad_rule_type(loader_test_init, logger):
    mule, cfg_loader = loader_test_init
    cfg_loader.config = {
        'rules': [
            {
                'name': 'test',
                'type': 'dwaawwadwadaw',
                'record': 'A',
            },
        ]
    }
    mule.rules = Rules()

    from dnsmule import loader
    logger.mock_in_module(loader)

    cfg_loader.append_rules()
    assert 'error' in logger.result


def test_plugin_fails(logger, loader_test_init):
    mule, cfg_loader = loader_test_init
    cfg_loader.config = {
        'plugins': [
            {
                'name': 'awddawdwadawdaw.dwadwadwadwadwa'
            },
        ]
    }
    mule.plugins = Plugins()

    from dnsmule import loader
    logger.mock_in_module(loader)

    cfg_loader.append_plugins()
    assert 'error' in logger.result


def test_loading_rules_twice_raises_on_duplicate(loader_test_init):
    mule, loader = loader_test_init
    loader.config = {
        'rules': [
            {
                'name': 'test',
                'type': 'dns.regex',
                'record': 'A',
                'config': {
                    'pattern': 'a',
                }
            },
        ]
    }
    mule.rules = Rules()
    loader.append_rules()
    with pytest.raises(ValueError):
        loader.append_rules()


def test_loading_rules_name_taken_from_config(loader_test_init):
    mule, loader = loader_test_init
    loader.config = {
        'rules': [
            {
                'name': 'test',
                'type': 'dns.regex',
                'record': 'A',
                'config': {
                    'name': 'Verbose Test Rule',
                    'pattern': 'a',
                }
            },
        ]
    }
    mule.rules = Rules()
    loader.append_rules()
    assert mule.rules.contains('A', 'Verbose Test Rule'), 'Failed to set correct name'


def test_loading_rules_initializes_dynamic(loader_test_init):
    from textwrap import dedent
    mule, loader = loader_test_init
    loader.config = {
        'rules': [
            {
                'name': 'test',
                'type': 'dns.dynamic',
                'record': 'A',
                'config': {
                    'code': dedent(
                        """
                        def init():
                            add_rule(
                                "A",
                                "dns.regex",
                                "init_rule",
                                pattern="test",
                            )
                        """
                    )
                }
            },
        ]
    }
    mule.rules = Rules()
    loader.append_rules()
    assert mule.rules.contains('A', 'init_rule'), 'Failed to call dynamic init'


def test_loading_rules_initializes_nested_dynamic(loader_test_init):
    from textwrap import dedent
    mule, loader = loader_test_init
    loader.config = {
        'rules': [
            {
                'name': 'test',
                'type': 'dns.dynamic',
                'record': 'A',
                'config': {
                    'code': dedent(
                        """
                        def init():
                            from textwrap import dedent
                            add_rule(
                                "A",
                                "dns.dynamic",
                                "init_rule",
                                code=dedent(
                                    '''
                                    def init():
                                        add_rule(
                                            "a",
                                            "dns.regex",
                                            "init_recursive",
                                            pattern="a",
                                        )
                                    '''
                                ),
                            )
                        """
                    )
                }
            },
        ]
    }
    mule.rules = Rules()
    loader.append_rules()
    assert mule.rules.contains('A', 'init_rule'), 'Failed to call dynamic init'
    assert mule.rules.contains('A', 'init_recursive'), 'Failed to call dynamic init for recursive dynamic rules'


def test_loading_error_gets_logged(logger, loader_test_init):
    mule, cfg_loader = loader_test_init
    cfg_loader.config = {
        'rules': [
            {
                'name': 'test',
                'type': 'dns.dynamic',
                'record': 'A',
                'config': {
                    'code': 'this is a syntax error'
                }
            },
        ]
    }

    from dnsmule import loader
    logger.mock_in_module(loader)

    mule.rules = Rules()
    cfg_loader.append_rules()
    assert 'error' in logger.result


def test_plugins_loading_twice_does_not_affect_loaded(loader_test_init):
    mule, loader = loader_test_init
    loader.config = {
        'plugins': [
            {
                'name': 'dnsmule.plugins.noop.NOOPPlugin',
            }
        ]
    }
    mule.plugins = Plugins()
    loader.append_plugins()

    assert mule.plugins.contains(NOOPPlugin), 'Failed to contain plugin'
    plugin = mule.plugins.get(NOOPPlugin)

    loader.config = {
        'plugins': [
            {
                'name': 'dnsmule.plugins.noop.NOOPPlugin',
                'config': {
                    'a': 1,
                }
            }
        ]
    }
    loader.append_plugins()
    assert mule.plugins.get(NOOPPlugin) is plugin, 'Plugin got overridden'


def test_storage_fallback(loader_test_init, logger):
    from dnsmule import loader as m
    logger.mock_in_module(m)

    mule, loader = loader_test_init
    loader.config = {
        'storage': {
            'name': 'dnsmule.backends.noop.dwadawdwadwawa',
            'fallback': True,
        }
    }
    loader.set_storage()
    assert type(mule.storage) == DictStorage, 'Failed to default'
    assert 'error' in logger.result


def test_storage_without_fallback(loader_test_init, logger):
    mule, loader = loader_test_init
    loader.config = {
        'storage': {
            'name': 'dnsmule.backends.noop.dwadawdwadwawa',
        }
    }

    with pytest.raises(ImportError):
        loader.set_storage()
