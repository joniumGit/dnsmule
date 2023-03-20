from dataclasses import dataclass, InitVar
from typing import Dict, Union, Any, Iterable, Collection, Container

from ..definitions import Result, Domain, RRType


@dataclass
class Query:
    ANY = Any
    data: Dict[str, Union[Any, Container[Any]]] = ANY
    domains: Collection[Union[str, Domain]] = ANY
    types: InitVar[Iterable[Union[str, int, RRType]]] = ANY
    tags: Collection[str] = ANY

    def __post_init__(self, types: Iterable[Union[str, int, RRType]]):
        self._types = {RRType.from_any(o) for o in types} if types is not Query.ANY else Query.ANY

    def _check_data(self, r: Result) -> bool:
        if self.data is not Query.ANY:
            for k in filter(r.data.__contains__, self.data):
                search_value = self.data[k]
                if search_value is Query.ANY:
                    return True
                else:
                    v = r.data[k]
                    return (
                            v == search_value
                            or hasattr(v, '__contains__') and search_value in v
                            or hasattr(search_value, '__contains__') and v in search_value
                    )
            return False
        else:
            return True

    def _check_tags(self, r: Result) -> bool:
        return self.tags is Query.ANY or any(map(self.tags.__contains__, r.tags))

    def _check_types(self, r: Result) -> bool:
        return self._types is Query.ANY or any(map(self._types.__contains__, r.type))

    def _check_domains(self, r: Result) -> bool:
        return self.domains is Query.ANY or r.domain in self.domains

    def __call__(self, r: Result) -> bool:
        return self._check_domains(r) and self._check_types(r) and self._check_tags(r) and self._check_data(r)


__all__ = [
    'Query',
]
