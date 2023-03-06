from pathlib import Path
from typing import Type, Union

from .abstract import Backend
from ..rules import Rules


def find_backend(backend: str) -> Type[Backend]:
    module, _, cls = backend.partition('.')

    import importlib
    try:
        m = importlib.import_module(f'.{module}', package=__package__)
    except ImportError:
        m = importlib.import_module(module)

    return getattr(m, cls)


def load_config(file: Union[str, Path], rules: Rules) -> Backend:
    """Loads backend from yaml config
    """
    import yaml
    with open(file, 'r') as f:
        document = yaml.safe_load(f)
        backend = document['backend']
        return find_backend(backend['name'])(rules, **backend.get('config', {}))


__all__ = [
    'find_backend',
    'Backend',
    'load_config',
]
