import re
from dataclasses import dataclass, InitVar
from typing import Union, Any, Iterable, Collection

from ..definitions import Result, Domain, RRType


@dataclass
class Query:
    ANY = Any
    domains: Collection[Union[str, Domain]] = ANY
    types: InitVar[Iterable[Union[str, int, RRType]]] = ANY
    tags: InitVar[str] = ANY
    data: InitVar[str] = ANY

    def __post_init__(self, types: Iterable[Union[str, int, RRType]], tags: str, data: str):
        self._tags = re.compile(tags, flags=re.UNICODE) if tags is not Query.ANY else Query.ANY
        self._data = re.compile(data, flags=re.UNICODE) if data is not Query.ANY else Query.ANY
        self._types = {RRType.from_any(o) for o in types} if types is not Query.ANY else Query.ANY

    def _check_data(self, r: Result) -> bool:
        return self._data is Query.ANY or self._data.search(str(r.data))

    def _check_tags(self, r: Result) -> bool:
        return self._tags is Query.ANY or any(
            self._tags.search(t)
            for t in r.tags
        )

    def _check_types(self, r: Result) -> bool:
        return self._types is Query.ANY or any(
            t in self._types
            for t in r.type
        )

    def _check_domains(self, r: Result) -> bool:
        return self.domains is Query.ANY or r.domain in self.domains or any(
            r.domain.endswith(domain[1:])
            for domain in self.domains
            if domain.startswith('*')
        )

    def __call__(self, r: Result) -> bool:
        return self._check_domains(r) and self._check_types(r) and self._check_tags(r) and self._check_data(r)


__all__ = [
    'Query',
]
