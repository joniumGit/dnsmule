from dataclasses import dataclass

from .data import Data
from .domain import Domain
from .result import Result
from .rrtype import RRType


@dataclass(slots=True, frozen=False)
class Record:
    domain: Domain
    type: RRType
    data: Data
    _result: Result = None

    def result(self):
        if self._result is None:
            self._result = Result(self.type, self.domain)
        return self._result

    def identify(self, identification: str):
        r = self.result()
        r.tags.add(identification)
        return r

    def __hash__(self):
        return hash((self.type, self.domain))

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.domain == self.domain and other.type == self.type


__all__ = [
    'Record',
]
