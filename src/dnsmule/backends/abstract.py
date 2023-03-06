from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any, Union

from ..definitions import Domain, RRType, Result, Record
from ..rules import Rules


class Backend(ABC):

    def __init__(self, **kwargs):
        self.__dict__.update({
            k: v
            for k, v in kwargs.items()
            if not k.startswith('_')
        })

    async def run(self, rules: Rules, *targets: Union[str, Domain]) -> AsyncGenerator[Result, Any]:
        for target in targets:
            async for result in self.run_single(rules, target):
                yield result

    async def run_single(self, rules: Rules, target: Union[str, Domain]) -> AsyncGenerator[Result, Any]:
        types = rules.get_types()
        async for record in self.process(
                target if isinstance(target, Domain) else Domain(target),
                *types
        ):
            yield await rules.process_record(record)

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
