from dataclasses import dataclass
from typing import Dict, List

from .domain import Domain
from .rrtype import RRType


@dataclass(slots=True, init=False, frozen=False)
class Result:
    domain: Domain
    type: RRType
    tags: List
    data: Dict

    # noinspection PyShadowingBuiltins
    def __init__(self, type: RRType, domain: Domain):
        self.type = type
        self.domain = domain
        self.tags = []
        self.data = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __add__(self, other: 'Result') -> 'Result':
        if self is not other:
            if self.type != other.type:
                raise ValueError('Can not add different types')
            self.tags.extend(other.tags)
            self.data.update(other.data)
        return self

    def __bool__(self):
        return bool(self.tags or self.data)

    def __hash__(self):
        return hash((self.type, self.domain))

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.domain == self.domain and other.type == self.type


__all__ = [
    'Result',
]
