from abc import ABC, abstractmethod
from typing import Iterable, AsyncGenerator, Any

from ..definitions import Domain, RRType, Result, Record
from ..rules import Rules


class Backend(ABC):
    _rules: Rules

    def __init__(self, rules: Rules, **kwargs):
        self.__dict__.update({
            k: v
            for k, v in kwargs.items()
            if not k.startswith('_')
        })
        self._rules = rules

    async def run(self, targets: Iterable[Domain]) -> AsyncGenerator[Result, Any]:
        for target in targets:
            async for result in self.run_single(target):
                yield result

    async def run_single(self, target: Domain) -> AsyncGenerator[Result, Any]:
        types = self._rules.get_types()
        async for record in self.process(target, *types):
            yield await self._rules.process_record(record)

    @abstractmethod
    def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        pass
