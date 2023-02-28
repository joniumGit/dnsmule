from typing import Dict, Any

from ..utils import lmerge


class Domain:
    name: str
    data: Dict[str, Any]

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.data = {**kwargs}

    def __add__(self, other: 'Domain'):
        if self.name != other.name and not self.is_subdomain(other):
            raise ValueError('Can not add two different domains')
        lmerge(self.data, other.data)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Domain) and other.name == self.name or other == self.name

    def is_subdomain(self, other: 'Domain'):
        parts_self = self.name.split('.')
        parts_other = other.name.split('.')
        return parts_other[-len(parts_self):] == parts_self

    @classmethod
    def from_text(cls, value: str):
        return cls(value)

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
