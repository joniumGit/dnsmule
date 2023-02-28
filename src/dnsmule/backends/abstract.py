from abc import ABC, abstractmethod
from typing import Iterable, AsyncGenerator, Any

from ..definitions import Domain, RRType, Result, Record
from ..rules import Rules


class Backend(ABC):
    rules: Rules

    def __init__(self, rules: Rules):
        self.rules = rules

    async def run(self, targets: Iterable[Domain]) -> AsyncGenerator[Result, Any]:
        for target in targets:
            async for result in self.run_single(target):
                yield result

    async def run_single(self, target: Domain) -> AsyncGenerator[Result, Any]:
        types = self.rules.get_types()
        async for record in self.process(target, *types):
            yield self.rules.process_record(record)

    @abstractmethod
    def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        pass
