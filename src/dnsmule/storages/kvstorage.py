from abc import ABC, abstractmethod
from typing import Optional, Iterable, List, Union, Mapping

from .abstract import Storage, Query
from ..definitions import Result, Domain, RRType

JsonData = Mapping[str, Union[List, str, int, float, 'Json']]


def result_to_json_data(result: Result) -> JsonData:
    return {
        'domain': result.domain,
        'type': [
            str(RRType.from_any(t))
            for t in sorted(result.type)
        ],
        'tags': [*result.tags],
        'data': result.data
    }


def result_from_json_data(data: JsonData) -> Result:
    r = Result(domain=data['domain'])
    r.type.update(map(RRType.from_any, data.get('type', [])))
    r.tags.update(data.get('tags', []))
    r.data.update(data.get('data', {}))
    return r


class KeyValueStorage(Storage, ABC):
    _prefix = 'STORAGE::RESULT::'

    def to_key(self, value: Domain) -> str:
        return f'{self._prefix}{value}'

    def from_key(self, value: str) -> Domain:
        return Domain(value.removeprefix(self._prefix))

    def is_key(self, value: str) -> bool:
        return value.startswith(self._prefix)

    @abstractmethod
    def _set(self, key: str, value: JsonData) -> None:
        """Set a value
        """

    @abstractmethod
    def _get(self, key: str) -> Optional[JsonData]:
        """Get a value
        """

    @abstractmethod
    def _del(self, key: str) -> None:
        """Delete a value
        """

    @abstractmethod
    def _iterate(self) -> Iterable[str]:
        """Iterate keys
        """

    def domains(self) -> Iterable[Domain]:
        yield from map(self.from_key, filter(self.is_key, self._iterate()))

    def contains(self, key: Domain) -> bool:
        return self.fetch(key) is not None

    def store(self, result: Result):
        self._set(self.to_key(result.domain), result_to_json_data(result))

    def fetch(self, domain: Domain):
        result = self._get(self.to_key(domain))
        if result:
            return result_from_json_data(result)

    def delete(self, domain: Domain) -> None:
        self._del(self.to_key(domain))

    def results(self) -> Iterable[Result]:
        yield from map(self.fetch, self.domains())

    def query(self, query: Query) -> Iterable[Result]:
        yield from filter(query, self.results())


__all__ = [
    'KeyValueStorage',
    'JsonData',
    'Query',
    'result_to_json_data',
    'result_from_json_data',
]
