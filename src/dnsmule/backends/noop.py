from typing import Iterable

from .abstract import Backend
from ..definitions import Domain, Record, RRType
from ..utils import empty


class NOOPBackend(Backend):

    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        """No-op"""
        yield from empty()


__all__ = [
    'NOOPBackend',
]
