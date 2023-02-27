from dataclasses import dataclass
from typing import Dict, List, Callable

from ._compat import Type, Data, Domain
from ..utils import Comparable


@dataclass(slots=True, init=False, frozen=False)
class Result:
    type: Type
    tags: List
    data: Dict
    domain: Domain

    def __init__(self, _type: Type, _domain: Domain):
        self.type = _type
        self.domain = _domain
        self.tags = []
        self.data = {}

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __add__(self, other: 'Result') -> 'Result':
        if self is not other:
            if self.type != other.type:
                raise ValueError('Can not add different types')
            self.tags.extend(other.tags)
            self.data.update(other.data)
        return self

    def __bool__(self):
        return bool(self.tags or self.data)

    def __hash__(self):
        return hash((self.type, self.domain))

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.domain == self.domain and other.type == self.type


@dataclass(slots=True, frozen=False)
class Record:
    domain: Domain
    type: Type
    data: Data
    _result: Result = None

    def result(self):
        if self._result is None:
            self._result = Result(self.type, self.domain)
        return self._result

    def identify(self, identification: str):
        r = self.result()
        r.tags.append(identification)
        return r

    def __hash__(self):
        return hash((self.type, self.domain))

    def __eq__(self, other):
        return isinstance(other, type(self)) and other.domain == self.domain and other.type == self.type


RuleFunction = Callable[[Record], Result]


class Rule(metaclass=Comparable, key='priority', reverse=True):
    """Wrapper class for rules to support priority based comparison
    """
    f: RuleFunction

    name: str = None
    priority: int = 0

    def __init__(self, f: RuleFunction = None, **kwargs):
        super().__init__()
        _keys = {
            k: v
            for k, v in kwargs.items()
            if not (k.startswith('__') and k.endswith('__'))
        }
        self.__dict__.update(_keys)
        self._properties = [*_keys.keys()]
        if f is not None and not callable(f):
            raise ValueError('Rule function not callable')
        elif f is None and self.__call__ is not Rule.__call__:
            self.f = self.__call__
        else:
            if f is None:
                raise ValueError('Rule function was None')
            self.f = f
            if not self.name and hasattr(self.f, '__name__'):
                self.name = self.f.__name__

    def __call__(self, record: Record):
        if self.f is self.__call__:
            raise RecursionError('Illegal state, infinite recursion detected')
        return self.f(record)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        args = ','.join(
            f'{k}={repr(self.v)}'
            for k in self._properties
        )
        return f'{type(self.name)}({args})'


RuleFactory = Callable[[str, Dict], Rule]


class RuleCreator:
    """Helper for rule registration
    """
    priority: int
    rtype: str
    callback: Callable[[Type, Rule], None]

    def __init__(self, callback: Callable[[Type, Rule], None], rtype: str = None, priority: int = 0):
        super().__init__()
        self.rtype = rtype
        self.priority = priority
        self.callback = callback

    def __call__(self, f: RuleFunction):
        if self.rtype is None:
            raise ValueError('Rule requires a record type')
        self.callback(Type.from_any(self.rtype), Rule(f=f, priority=self.priority))
        return f

    def __getitem__(self, priority: int):
        if self.priority is not None:
            raise ValueError('Rule already has a priority')
        return type(self)(self.callback, priority=priority)

    def __getattr__(self, rtype: str):
        if self.rtype is not None:
            raise ValueError('Rule already has a type')
        return type(self)(self.callback, rtype=rtype)


__all__ = [
    'Result',
    'Record',
    'Domain',
    'Rule',
    'RuleCreator',
    'Type',
    'Data',
    'RuleFactory',
]
