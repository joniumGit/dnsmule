from typing import Iterable

from ..api import Backend, Record, Domain, RRType


class NoOpBackend(Backend):
    """
    Does nothing
    """
    type = 'noop'

    def scan(self, domain: Domain, *types: RRType) -> Iterable[Record]:
        yield from []
