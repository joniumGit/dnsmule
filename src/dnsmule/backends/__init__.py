from pathlib import Path
from typing import Type, Union

from .abstract import Backend


def import_backend(backend: str) -> Type[Backend]:
    """Imports a module and gets the last part as attribute from it

    **Note:** This allows arbitrary imports and code execution
    """
    module, _, cls = backend.rpartition('.')

    import importlib
    try:
        m = importlib.import_module(f'.{module}', package=__package__)
    except ImportError:
        m = importlib.import_module(module)

    return getattr(m, cls)


def load_config(file: Union[str, Path]) -> Backend:
    """Loads backend from yaml config
    """
    import yaml
    with open(file, 'r') as f:
        document = yaml.safe_load(f)
        backend = document['backend']
        return import_backend(backend['name'])(**backend.get('config', {}))


__all__ = [
    'import_backend',
    'Backend',
    'load_config',
]
