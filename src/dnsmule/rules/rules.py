from typing import Dict, Union, List, Callable

from dns.message import Message
from dns.name import Name
from dns.rdata import Rdata as Data
from dns.rdatatype import RdataType as Type
from dns.rrset import RRset

from .comaparable import Comparable
from .data import Record, Result
from .types import RULE_TYPE
from .dynamic import DynamicRule


class Rule(metaclass=Comparable, key='priority', reverse=True):
    """Wrapper class for rules to support priority based comparison
    """

    def __init__(self, f: RULE_TYPE, priority: int):
        super().__init__()
        self.f = f
        self.priority = priority

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Rule(f={self.f.__name__ if self.f else None}, priority={self.priority})'


class RuleFactoryMixIn:
    _normal_handlers: Dict[str, Callable[..., RULE_TYPE]]
    _dynamic_handlers: Dict[str, DynamicRule]

    def __init__(self):
        self._normal_handlers = {}
        self._dynamic_handlers = {}

    def _get_dynamic_rules(self) -> Dict[str, DynamicRule]:
        return self._dynamic_handlers

    def _create_rule(self, **options) -> RULE_TYPE:
        """Creates a rule from rule config
        """
        rule_type = options.pop('type')
        if rule_type in self._normal_handlers:
            handler = self._normal_handlers[rule_type]
        else:
            handler = self._dynamic_handlers[rule_type]
        return handler(options.pop('name'), **options)

    def register(self, type_name: str, dynamic: bool = False):
        """Registers a handler for a rule type
        """

        def decorator(f):
            if dynamic:
                self._dynamic_handlers[type_name] = f
            else:
                self._normal_handlers[type_name] = f

        return decorator


class Rules(RuleFactoryMixIn):
    """Class for storing rules
    """
    _rules: Dict[Type, List[RULE_TYPE]]

    def __init__(self):
        super().__init__()

        from .factories import add_default  # Will only work here due to imports
        add_default(self)

        import logging
        self.log = logging.getLogger('dnsmule')

        self._rules = {
            dtype: []
            for dtype in Type
        }

    def _load_and_append_from_config(self, rule: Dict):
        self._append_to_rules(
            Type.from_text(rule.pop('record')),
            rule.pop('priority') if 'priority' in rule else 0,
            self._create_rule(**rule)
        )

    def load_config(self, config: List[Dict]):
        for rule in config:
            self._load_and_append_from_config(rule)

    def initialize_rules(self):
        for v in self._get_dynamic_rules().values():
            v.init(self._load_and_append_from_config)

    def process_record(self, record: Record) -> Result:
        result = Result(record.type)
        for r in self._rules.get(record.type, []):
            try:
                other_result = r(record)
                if other_result:
                    result += other_result
            except Exception as e:
                self.log.error(f'Rule {r.__name__} raised an exception', exc_info=e)
        return result

    def process_message(self, domain: Name, message: Message) -> Dict[Type, Result]:
        rrset: RRset
        rdata: Data
        out: Dict[Type, Result] = {t: Result(t) for t in Type}
        for rrset in message.answer:
            for rdata in rrset:
                out[rdata.rdtype] += self.process_record(Record(
                    type=rdata.rdtype,
                    domain=domain,
                    data=rdata,
                ))
        return out

    def _append_to_rules(self, rtype: Type, priority: int, f: RULE_TYPE):
        if rtype not in self._rules:  # IF unknown types are added
            self._rules[rtype] = []
        self._rules[rtype].append(Rule(f, priority=priority))
        self._rules[rtype].sort()

    def add_rule(self, rtype: Union[Type, int], priority: int):
        def decorator(f: RULE_TYPE):
            self._append_to_rules(rtype, priority, f)
            return f

        return decorator

    def __getattr__(self, rtype: str):
        return getattr(RuleCreator(self), rtype)

    def __getitem__(self, item: Type):
        return self._rules[item]


class RuleCreator:
    """Helper for rule registration
    """

    def __init__(self, rules: Rules, rtype: Type = None, priority: int = 0):
        super().__init__()
        self.rtype = rtype
        self.priority = priority
        self.rules = rules

    def __call__(self, f: RULE_TYPE):
        if self.rtype is None:
            raise ValueError('rule requires a record type')
        self.rules.add_rule(self.rtype, priority=self.priority)(f)

    def __getitem__(self, priority: int):
        return type(self)(self.rules, priority=priority)

    def __getattr__(self, rtype: str):
        return type(self)(self.rules, rtype=Type.from_text(rtype))


__all__ = [
    'Rule',
    'Rules',
]
