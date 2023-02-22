from typing import Dict, Union, List, Callable

from dns.message import Message
from dns.name import Name
from dns.rdata import Rdata as Data
from dns.rdatatype import RdataType as Type
from dns.rrset import RRset

from .comaparable import Comparable
from .data import Record, Result
from .types import RULE_TYPE

RULES: Dict[Type, List[RULE_TYPE]] = {
    dtype: []
    for dtype in Type
}


def invoke(record: Record):
    result = Result(record.type)
    for r in RULES.get(record.type, []):
        try:
            other_result = r(record)
            if other_result:
                result = result.merge(other_result)
        except Exception as e:
            import logging
            import inspect
            logging.getLogger('dnsmule').error(f'Rule {r.__name__} raised an exception', exc_info=e)


def process(domain: Name, message: Message):
    rrset: RRset
    rdata: Data
    for rrset in message.answer:
        for rdata in rrset:
            invoke(Record(
                type=rdata.type,
                domain=domain,
                data=rdata,
            ))


def _add_rule(rtype: Type, priority: int, f):
    if rtype not in RULES:  # IF unknown types are added
        RULES[rtype] = []
    RULES[rtype].append(Rule(f, priority=priority))
    RULES[rtype].sort()


def add_rule(rtype: Union[Type, int], priority: int):
    def decorator(f):
        _add_rule(rtype, priority, f)
        return f

    return decorator


class Rule(metaclass=Comparable, key='priority', reverse=True):
    """Wrapper class for rules to support priority based comparison
    """

    def __init__(self, f: RULE_TYPE, priority: int):
        self.f = f
        self.priority = priority

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'<Rule name={self.f.__name__ if self.f else None} priority={self.priority}>'


class RuleFactory:
    """Helper for rule registration
    """

    def __init__(self, rtype: Type = None, priority: int = 0):
        self.rtype = rtype
        self.priority = priority

    def __call__(self, f):
        if self.rtype is None:
            raise ValueError('rule requires a record type')
        return add_rule(self.rtype, priority=self.priority)(f)

    def __getitem__(self, priority: int):
        return type(self)(priority=priority)

    def __getattr__(self, rtype: str) -> Callable[[RULE_TYPE], RULE_TYPE]:
        return type(self)(rtype=Type.from_text(rtype))


rule = RuleFactory()

__all__ = [
    'rule',
    'process',
]
