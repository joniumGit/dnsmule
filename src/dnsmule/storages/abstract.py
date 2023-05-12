import contextlib
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import MutableMapping, Iterator, Optional, Iterable, List, Mapping, Union, Literal, Generic, TypeVar, \
    Collection

from ..baseclasses import KwargClass
from ..definitions import Result, Domain, RRType

T = TypeVar('T')


@dataclass
class Query:
    """
    Searches for results

    Storage implementations can provide additional query functionality by extending this class

    **Note:** All searches are case-sensitive by default
    """

    domains: Iterable[Union[str, Domain]] = None
    """
    Collection of domains in the following forms:

    - subdomain.domain.tld
    - *.domain.tld
    """

    types: Iterable[Union[str, int, RRType]] = None
    """
    Collection of Resource Record types to query.
    
    The types can be RRType, int, or str type
    """

    tags: Iterable[str] = None
    """
    Search the result tag
    
    This collection allows for wildcard matches in tags using the '*' character::
    
        DNS::REGEX::*
        *::EU-FRA1
        *::REGEX::*

    The tags are usually in the format::
    
        MODULE::TYPE::NAME(::DATA){0,n}
    
    The checks are done as follows:
    
        search == tag or tags.startswith(search) or tag.endswith(tag)
    
    Searching for matches in a lot of string which are not bound might produce bad matches and consume time.
    """

    data: Iterable[str] = None
    """
    Provider search capability for keys of data
    
    No further search capability is provided here, but drivers are free to expand this
    """


class WildcardCollection(Generic[T]):
    """
    Collection of values with wildcards

    The wildcard values will also serve as exact matches
    """

    def __init__(self, values: Iterable[T]):
        self.exact = {*values}
        self.prefix = []
        self.suffix = []
        self.search = []
        for value in self.exact:
            stars = value.count('*')
            if stars > 1:
                self.search.append(re.compile(re.escape(value).replace(re.escape('*'), '.*'), flags=re.UNICODE))
            elif stars == 1 and value.endswith('*'):
                self.prefix.append(value[:-1])
            elif stars == 1 and value.startswith('*'):
                self.suffix.append(value[1:])

    def __contains__(self, item: T) -> bool:
        return (
                item in self.exact
                or any(item.startswith(prefix) for prefix in self.prefix)
                or any(item.endswith(suffix) for suffix in self.suffix)
                or any(pattern.search(item) for pattern in self.search)
        )


class BasicSearch:
    """Implements basic search capability
    """
    domains: Union[WildcardCollection, Literal[False]]
    types: Union[Collection[RRType], Literal[False]]
    tags: Union[WildcardCollection, Literal[False]]
    data: Union[Collection[str], Literal[False]]

    def __init__(self, query: Query):
        self.domains = WildcardCollection(query.domains) if query.domains else False
        self.types = {*map(RRType.from_any, query.types)} if query.types else False
        self.tags = WildcardCollection(query.tags) if query.tags else False
        self.data = {*query.data} if query.data else False

    def __call__(self, r: Result):
        return (
                (not self.domains or r.domain in self.domains)
                and (not self.types or any(map(self.types.__contains__, r.type)))
                and (not self.tags or any(map(self.tags.__contains__, r.tags)))
                and (not self.data or any(map(self.data.__contains__, r.data.keys())))
        )


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
        query = BasicSearch(query)
        yield from filter(query, self.results())


__all__ = [
    'Storage',
    'Query',
    'BasicSearch',
    'PrefixedKeyValueStorage',
    'JsonData',
    'Query',
    'result_to_json_data',
    'result_from_json_data',
    'WildcardCollection',
]
