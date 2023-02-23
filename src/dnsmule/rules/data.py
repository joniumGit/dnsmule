from dataclasses import dataclass
from typing import Dict, List

from dns.name import Name
from dns.rdata import Rdata as Data
from dns.rdatatype import RdataType as Type


class Result:
    type: Type
    tags: List
    data: Dict

    __slots__ = ['type', 'tags', 'data']

    def __init__(self, __type: Type):
        self.type = __type
        self.tags = []
        self.data = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __add__(self, other: 'Result') -> 'Result':
        r = Result(self.type)
        r.tags.extend(self.tags)
        r.tags.extend(other.tags)
        r.data.update(self.data)
        r.data.update(other.data)
        return r

    def __bool__(self):
        return self.tags or self.data


@dataclass
class Record:
    type: Type
    domain: Name
    data: Data

    def result(self):
        return Result(self.type)

    def identify(self, identification: str):
        r = self.result()
        r.tags.append(identification)
        return r


__all__ = [
    'Result',
    'Record',
    'Name',
    'Data',
    'Type',
]
