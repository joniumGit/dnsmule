from dataclasses import dataclass
from typing import Union

from .data import Data
from .domain import Domain
from .result import Result
from .rrtype import RRType


@dataclass(slots=True, frozen=False, init=False)
class Record:
    domain: Domain
    type: RRType
    data: Data
    _result: Result

    # noinspection PyShadowingBuiltins
    def __init__(self, domain: Union[str, Domain], type: RRType, data: Union[str, Data]):
        self.domain = domain if isinstance(domain, Domain) else Domain(name=domain)
        self.type = type
        self.data = data if isinstance(data, Data) else Data(type=type, value=data)
        if self.data.type != self.type:
            raise ValueError('Data was not the same RRtype', self.type, self.data.type)
        self._result = None

    def result(self):
        if self._result is None:
            self._result = Result(self.domain, self.type)
        return self._result

    def identify(self, identification: str):
        r = self.result()
        r.tags.add(identification)
        return r

    def __hash__(self):
        return hash((self.domain, self.type))

    def __eq__(self, other: 'Record'):
        return isinstance(other, Record) and other.domain == self.domain and other.type == self.type

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data


__all__ = [
    'Record',
]
