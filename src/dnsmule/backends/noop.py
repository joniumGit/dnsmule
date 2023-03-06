from typing import AsyncGenerator, Any

from .abstract import Backend
from .. import RRType
from ..definitions import Domain, Record


class NOOPBackend(Backend):

    async def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:  # pragma: nocover
        """No-op"""
        for o in []:
            yield o


__all__ = [
    'NOOPBackend',
]
