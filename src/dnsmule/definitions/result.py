from dataclasses import dataclass
from typing import Dict, Set, Union, List, Optional

from .domain import Domain
from .rrtype import RRType
from .tag import Tag
from ..utils import left_merge, Comparable

ResultData = Dict[str, Union['ResultData', List, str, int, float]]


@dataclass(frozen=False, init=False, repr=True, eq=False, unsafe_hash=False)
class Result(Comparable):
    domain: Domain
    type: Set[RRType]
    tags: Set[Tag]
    data: ResultData

    # noinspection PyShadowingBuiltins
    def __init__(self, domain: Domain, initial_type: RRType = None):
        self.type = set()
        if initial_type:
            self.type.add(initial_type)
        self.domain = domain
        self.tags = set()
        self.data = {}

    def tag(self, tag: Union[str, Tag]):
        self.tags.add(tag)

    def __add__(self, other: 'Result') -> 'Result':
        if other is None or other is self:
            return self
        elif not isinstance(other, Result):
            raise TypeError(f'Can not add Result and {type(other)}')
        elif self.domain != other.domain:
            raise ValueError('Can not add different domains')
        else:
            self.type.update(other.type)
            self.tags.update(other.tags)
            left_merge(self.data, other.data)
            return self

    def __bool__(self):
        return bool(self.tags or self.data)

    def __hash__(self):
        return hash(self.domain)

    def __eq__(self, other: 'Result'):
        return isinstance(other, Result) and other.domain == self.domain or other == self.domain

    def __contains__(self, item):
        return item in self.tags

    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        return iter(self.tags)

    def __lt__(self, other: 'Result'):
        return self.domain < other.domain

    def __getitem__(self, item: str) -> Optional[ResultData]:
        return self.data[item]

    def __setitem__(self, key: str, value: Union[ResultData, List, str, int, float]) -> None:
        self.data[key] = value


__all__ = [
    'Result',
    'ResultData',
]
