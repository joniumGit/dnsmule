from abc import ABC, abstractmethod
from typing import List


class Comparable(ABC):

    @abstractmethod
    def __lt__(self, other):
        """Implement to support sorting
        """


class KwargClass:
    _properties: List[str]

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


class classproperty(classmethod):

    def __init__(self, f):
        super(classproperty, self).__init__(property(f))

    def __set__(self, instance, value):
        raise AttributeError('classproperty')

    def __delete__(self, instance):
        raise AttributeError('classproperty')


class Identifiable:
    _id: str = None
    id: str

    @classproperty
    def id(cls) -> str:
        if cls._id:
            return cls._id
        else:
            return f'{cls.__module__}.{cls.__qualname__}'


__all__ = [
    'Comparable',
    'KwargClass',
    'classproperty',
    'Identifiable',
]
