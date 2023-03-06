from typing import Dict, Any, Union

from ..utils import Comparable


class Domain(metaclass=Comparable, key='name'):
    name: str
    data: Dict[str, Any]

    def __init__(self, name: str, **kwargs):
        self.name = str(name)
        self.data = {**kwargs}

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: 'Domain'):
        return isinstance(other, Domain) and other.name == self.name or other == self.name

    def is_subdomain(self, other: Union['Domain', str]):
        """True if the 'other' value is a subdomain of this
        """
        if isinstance(other, str):
            other = Domain(other)
        parts_self = self.name.split('.')
        parts_other = other.name.split('.')
        return len(parts_self) < len(parts_other) and parts_other[-len(parts_self):] == parts_self

    def __str__(self):
        return self.name

    def __repr__(self):
        if self.data:
            args = ','.join(f'{k}={repr(v)}' for k, v in self.data.items())
            return f'{type(self).__name__}(name={repr(self.name)},{args})'
        else:
            return f'{type(self).__name__}(name={repr(self.name)})'


__all__ = [
    'Domain',
]
