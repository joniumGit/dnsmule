import contextlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import MutableMapping, Iterator, Optional, Iterable, List, Mapping, Union, Any, Collection

from ..definitions import Result, Domain, RRType
from ..utils import KwargClass


@dataclass
class Query:
    domains: Collection[Union[str, Domain]] = None
    """
    Collection of domains in the following forms:

    - subdomain.domain.tld
    - *.domain.tld
    """

    types: Collection[Union[str, int, RRType]] = None
    """Collection of Resource Record types to query.
    """

    tags: str = None
    """Search the tags using regex

    The tags are in teh format MODULE::TYPE::NAME(::DATA)*
    """

    data: Any = None
    """This is used to query the Data attribute in the Result

    NotImplementedError if this is not implemented in storage driver
    """


class DefaultQuerier:
    """Implements crude search capability
    """

    domains: Collection[str]
    types: Collection[str]
    tags: re.Pattern
    data: re.Pattern

    @classmethod
    def create(cls, query: Query):
        return cls(query)

    def __init__(self, query: Query):
        self.domains = {*query.domains} if query.domains else None
        self.types = {RRType.from_any(o) for o in query.types} if query.types else None
        self.tags = re.compile(query.tags, flags=re.UNICODE) if query.tags else None
        self.data = re.compile(str(query.data), flags=re.UNICODE) if query.data else None

    def check_data(self, r: Result) -> bool:
        return not self.data or self.data.search(str(r.data))

    def check_tags(self, r: Result) -> bool:
        return not self.tags or any(
            self.tags.search(t)
            for t in r.tags
        )

    def check_types(self, r: Result) -> bool:
        return not self.types or any(
            t in self.types
            for t in r.type
        )

    def check_domains(self, r: Result) -> bool:
        return not self.domains or r.domain in self.domains or any(
            r.domain.endswith(domain[1:])
            for domain in self.domains
            if domain.startswith('*')
        )

    def __call__(self, r: Result) -> bool:
        return self.check_domains(r) and self.check_types(r) and self.check_tags(r) and self.check_data(r)


class StorageBase(KwargClass, ABC):

    @abstractmethod
    def size(self) -> int:
        """Estimate the size of this storage
        """

    @abstractmethod
    def contains(self, domain: Domain) -> bool:
        """Check if value exists
        """

    @abstractmethod
    def store(self, result: Result) -> None:
        """Store a result into storage
        """

    @abstractmethod
    def fetch(self, domain: Domain) -> Optional[Result]:
        """Fetch a result for a domain
        """

    @abstractmethod
    def delete(self, domain: Domain) -> None:
        """Delete a domain
        """

    @abstractmethod
    def results(self) -> Iterable[Result]:
        """Iterate through all results
        """

    @abstractmethod
    def domains(self) -> Iterable[Domain]:
        """Iterate through all domains
        """

    @abstractmethod
    def query(self, query: Query) -> Iterable[Result]:
        """Query a result
        """

    @contextlib.contextmanager
    def using(self, result: Result) -> Result:
        result += self.fetch(result.domain)
        yield result
        self.store(result)


class Storage(MutableMapping[Domain, Result], StorageBase, ABC):
    """Supports using storage like a mapping
    """

    def __setitem__(self, key: Union[str, Domain], value: Result) -> None:
        if key != value.domain:
            raise ValueError('Domain Mismatch', key, value.domain)
        self.store(value)

    def __delitem__(self, key: Union[str, Domain]) -> None:
        self.delete(key)

    def __getitem__(self, key: Union[str, Domain]) -> Result:
        return self.fetch(key)

    def __len__(self) -> int:
        return self.size()

    def __iter__(self) -> Iterator[Domain]:
        yield from self.domains()

    def __contains__(self, o: object) -> bool:
        return isinstance(o, str) and self.contains(Domain(o))


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


class PrefixedKeyValueStorage(Storage, ABC):
    _prefix = 'STORAGE::RESULT::'

    def domain_to_key(self, value: Domain) -> str:
        return f'{self._prefix}{value}'

    def domain_from_key(self, value: str) -> Domain:
        return Domain(value.removeprefix(self._prefix))

    def matches_key_prefix(self, value: str) -> bool:
        """Checks if this value matches the key prefix
        """
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
        yield from map(self.domain_from_key, filter(self.matches_key_prefix, self._iterate()))

    def contains(self, key: Domain) -> bool:
        return self.fetch(key) is not None

    def store(self, result: Result):
        self._set(self.domain_to_key(result.domain), result_to_json_data(result))

    def fetch(self, domain: Domain):
        result = self._get(self.domain_to_key(domain))
        if result:
            return result_from_json_data(result)

    def delete(self, domain: Domain) -> None:
        self._del(self.domain_to_key(domain))

    def results(self) -> Iterable[Result]:
        yield from map(self.fetch, self.domains())

    def query(self, query: Query) -> Iterable[Result]:
        query = DefaultQuerier.create(query)
        yield from filter(query, self.results())


__all__ = [
    'Storage',
    'Query',
    'DefaultQuerier',
    'PrefixedKeyValueStorage',
    'JsonData',
    'Query',
    'result_to_json_data',
    'result_from_json_data',
]
