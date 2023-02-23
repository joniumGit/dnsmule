from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Any

from ._compat import Type, Data, Domain
from ..utils import Comparable


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
    domain: Domain
    type: Type
    data: Data

    def result(self):
        return Result(self.type)

    def identify(self, identification: str):
        r = self.result()
        r.tags.append(identification)
        return r


RuleFunction = Callable[[Record], Result]


class Rule(metaclass=Comparable, key='priority', reverse=True):
    """Wrapper class for rules to support priority based comparison
    """
    f: RuleFunction
    name: str
    priority: int

    def __init__(self, f: RuleFunction, priority: int = 0):
        super().__init__()
        self.f = f
        if hasattr(f, '__name__'):
            self.name = f.__name__
        self.priority = priority

    def __call__(self, record: Record):
        return self.f(record)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Rule(f={self.name}, priority={self.priority})'


RuleFactory = Callable[[str, Dict], Rule]


class DynamicRule(Rule):

    def __init__(self, code: str, **kwargs):
        self._globals = {
            '__builtins__': __builtins__,
            'Rule': RuleFunction,
            'Type': Type,
            'Record': Record,
            'Result': Result,
            'List': List,
            'Optional': Optional,
        }
        self._code = compile(code, 'dnsmule-dynamic-rule-init.py', 'exec')
        super().__init__(f=self.eval, **kwargs)

    def init(self, create_callback: RuleFactory):
        def add_rule(record_type: Any, rule_type: str, name: str, priority: int = 0, **options):
            create_callback(name, {
                'record': str(record_type),
                'type': rule_type,
                'priority': priority,
                **options,
            })

        self._globals['add_rule'] = add_rule
        exec(self._code, self._globals)
        eval('create()', self._globals)

    def eval(self, record: Record) -> Result:
        return eval('prepare(record)', self._globals, {'record': record}) or record.result()


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
    'DynamicRule',
    'RuleCreator',
    'Type',
    'Data',
    'RuleFactory',
]
