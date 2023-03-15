from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Union, Iterable

from ..definitions import Domain, RRType, Record


class Backend(ABC):

    def __init__(self, **kwargs):
        self.__dict__.update({
            k: v
            for k, v in kwargs.items()
            if not k.startswith('_')
        })

    async def run(self, targets: Iterable[Union[str, Domain]], *types: RRType) -> AsyncGenerator[Record, Any]:
        for target in targets:
            async for record in self.run_single(target, *types):
                yield record

    async def run_single(self, target: Union[str, Domain], *types: RRType) -> AsyncGenerator[Record, Any]:
        async for record in self.process(
                target if isinstance(target, Domain) else Domain(target),
                *types
        ):
            yield record

    @abstractmethod
    def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        """Abstract method for processing queries and producing records
        """

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.stop()

    async def start(self) -> None:
        """Startup method
        """

    async def stop(self) -> None:
        """Cleanup method
        """
