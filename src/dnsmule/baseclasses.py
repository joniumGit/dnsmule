from typing import List, Dict, Any


class KwargClass:
    """
    Class for taking in configuration parameters and others in kwargs

    Provides a property for getting the kwargs (_kwargs) and has a useful repr and str implementation.

    **Note:** All kwargs which start with a '_' are ignored.
    """
    _properties: List[str]
    _kwargs: Dict[str, Any]

    def __init__(self, **kwargs):
        properties = {
            k: v
            for k, v in kwargs.items()
            if not k.startswith('_')
        }
        self.__dict__.update(properties)
        self._properties = [k for k in properties]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        args = ','.join(
            f'{k}={repr(getattr(self, k))}'
            for k in self._properties
        )
        return f'{type(self).__name__}({args})'

    @property
    def _kwargs(self):
        return {
            k: getattr(self, k)
            for k in self._properties
        }


class Identifiable:
    id: str

    def __init_subclass__(cls):
        if not hasattr(cls, 'id'):
            cls.id = f'{cls.__module__}.{cls.__qualname__}'


__all__ = [
    'KwargClass',
    'Identifiable',
]
