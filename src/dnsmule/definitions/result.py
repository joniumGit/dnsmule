from dataclasses import dataclass
from typing import Dict, Set

from .domain import Domain
from .rrtype import RRType
from ..utils import lmerge


@dataclass(slots=True, init=False, frozen=False)
class Result:
    domain: Domain
    type: Set[RRType]
    tags: Set[str]
    data: Dict

    # noinspection PyShadowingBuiltins
    def __init__(self, domain: Domain, type: RRType = None):
        self.type = set()
        if type:
            self.type.add(type)
        self.domain = domain
        self.tags = set()
        self.data = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.tags

    def __add__(self, other: 'Result') -> 'Result':
        if not isinstance(other, Result):
            raise TypeError(f'Can not add Result and {type(other)}')
        if self is not other:
            if self.domain != other.domain:
                raise ValueError('Can not add different domains')
            self.type.update(other.type)
            self.tags.update(other.tags)
            lmerge(self.data, other.data)
        return self

    def __bool__(self):
        return bool(self.tags or self.data)

    def __hash__(self):
        return hash(self.domain)

    def __eq__(self, other: 'Result'):
        return isinstance(other, Result) and other.domain == self.domain or other == self.domain

    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        return iter(self.tags)

    def to_json(self):
        return {
            'domain': self.domain.name,
            'type': [
                RRType.to_text(t).removeprefix('RRType.') if isinstance(t, RRType) else t
                for t in map(RRType.from_any, sorted(self.type))
            ],
            'tags': [*self.tags],
            'data': self.data
        }


__all__ = [
    'Result',
]
