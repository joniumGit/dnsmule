from abc import ABC, abstractmethod
from typing import Iterable

from ..definitions import Domain, RRType, Record
from ..baseclasses import KwargClass


class Backend(KwargClass, ABC):

    def run(self, targets: Iterable[Domain], *types: RRType) -> Iterable[Record]:
        """Run DNS queries for given domains
        """
        for target in targets:
            for record in self.single(target, *types):
                yield record

    def single(self, target: Domain, *types: RRType) -> Iterable[Record]:
        """Run a DNS query for a single domain
        """
        for record in self._query(target, *types):
            yield record

    @abstractmethod
    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        """Abstract method for processing queries and producing records
        """


__all__ = [
    'Backend',
]
