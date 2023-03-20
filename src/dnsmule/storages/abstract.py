import contextlib
from abc import ABC, abstractmethod
from typing import Iterable, Optional, MutableMapping, Iterator, Union

from .query import Query
from ..definitions import Result, Domain
from ..utils import KwargClass


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


__all__ = [
    'Storage',
    'Query',
]
