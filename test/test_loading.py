from pathlib import Path

import pytest

from dnsmule.backends.noop import NOOPBackend
from dnsmule.loader import load_config, make_backend, make_plugins, make_rules, import_class
from dnsmule.plugins.noop import NOOPPlugin


def test_loading_empty_rules():
    assert load_config(Path(__file__).parent / 'sample_1.yml').rules is not None, 'Failed to create rules'


def test_loading_empty_plugins():
    assert load_config(Path(__file__).parent / 'sample_1.yml').plugins is not None, 'Failed to create plugins'


def test_loading_backend():
    cfg = load_config(Path(__file__).parent / 'sample_1.yml')
    assert type(cfg.backend()) == NOOPBackend, 'Failed relative import'


def test_loading_plugin():
    cfg = load_config(Path(__file__).parent / 'sample_1.yml', backend=False, plugins=True, rules=False)
    assert type(cfg.plugins[0]()) == NOOPPlugin, 'Failed plugin import'


def test_loading_false_is_none():
    cfg = load_config(
        Path(__file__).parent / 'sample_1.yml',
        backend=False,
        plugins=False,
        rules=False,
    )
    assert cfg.backend is cfg.rules is cfg.plugins is None, 'Had data'


def test_loading_makes_empty_ok():
    assert len(make_rules({})()) == 0, 'Failed to return empty rules'
    assert type(make_backend({})()) == NOOPBackend, 'Failed to return a default backend'
    assert make_plugins({}) == [], 'Failed to return empty collection'


def test_loading_backends_importing_from_module():
    assert type(make_backend({
        'backend': {
            'name': 'dnsmule.backends.noop.NOOPBackend'
        }
    })()) == NOOPBackend, 'Failed to import from anywhere'


def test_loading_backends_importing_fails():
    with pytest.raises(ImportError):
        make_backend({
            'backend': {
                'name': 'dawdwa.dwadwadawdwadaw.awdwdawdawdaw.NOTEXISTING'
            }
        })()


def test_loading_backends_importing_fails_attrib():
    with pytest.raises(ImportError):
        make_backend({
            'backend': {
                'name': 'dnsmule.backends.noop.NOTEXISTING'
            }
        })()


def test_loading_backends_importing_fails_attrib_relative():
    with pytest.raises(ImportError):
        make_backend({
            'backend': {
                'name': 'noop.NOTEXISTING'
            }
        })()


def test_loading_import_class_mismatch():
    with pytest.raises(ImportError):
        import_class('dnsmule.plugins.noop.NOOPPlugin', NOOPBackend, relative=False)


def test_loading_bad_rule_type(monkeypatch):
    def get_logger():
        raise IOError('test')

    with monkeypatch.context() as m:
        from dnsmule import loader
        m.setattr(loader, 'get_logger', get_logger)
        with pytest.raises(IOError):
            make_rules({
                'rules': [
                    {
                        'name': 'test',
                        'type': 'dwaawwadwadaw',
                        'record': 'A',
                    },
                ]
            })()


def test_loading_plugin_fails(monkeypatch):
    def get_logger():
        raise IOError('test')

    with monkeypatch.context() as m:
        from dnsmule import loader
        m.setattr(loader, 'get_logger', get_logger)
        with pytest.raises(IOError):
            make_plugins({
                'plugins': [
                    {
                        'name': 'awddawdwadawdaw.dwadwadwadwadwa'
                    },
                ]
            })
