from pathlib import Path

from dnsmule.backends import load_config, import_backend
from dnsmule.backends.noop import NOOPBackend
from dnsmule.rules import Rules


def test_backends_loading():
    be = load_config(Path(__file__).parent / 'sample_1.yml')
    assert type(be) == NOOPBackend, 'Failed relative import'


def test_backends_importing_from_module():
    assert import_backend('dnsmule.rules.Rules') == Rules, 'Failed to import from anywhere'
