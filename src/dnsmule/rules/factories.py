from typing import Dict, List
from typing import Union

from .entities import Rule, DynamicRule, Record, RuleFactory


class RuleFactoryMixIn:
    _factories: Dict[str, RuleFactory]

    def __init__(self):
        self._factories = {}
        add_default_factories(self)

    def create_rule(self, definition: Dict) -> Rule:
        """Creates a rule from rule config
        """
        return self._factories[definition.pop('type')](**definition)

    def register(self, type_name: str):
        """Registers a handler for a rule type
        """

        def decorator(f):
            self._factories[type_name] = f
            return f

        return decorator


def dns_create_regex_rule(
        pattern: str,
        priority: int = 0,
        identification: str = None,
        flags: List[str] = None,
        attribute: str = 'to_text',
        group: Union[int, str] = None,
        name: str = None,
        **__,
) -> Rule:
    import re
    import functools
    import operator

    all_flags = {k.lower(): v for k, v in re.RegexFlag.__members__.items()}
    flags = functools.reduce(
        operator.or_,
        (all_flags[flag.lower()] for flag in flags if flag in all_flags),
    )
    p = re.compile(pattern, flags=flags)

    def dns_regex(record: Record):
        m = p.search(str(getattr(record.data, attribute)))
        if m:
            _id = identification if group is None else m.group(group)
            return record.identify(f'DNS::REGEX::{_id.upper()}')

    if name:
        dns_regex.__name__ = name

    return Rule(dns_regex, priority=priority)


def dns_create_dynamic_rule(
        code: str,
        priority: int = 0,
        name: str = None,
        **__,
) -> DynamicRule:
    rule = DynamicRule(code, priority=priority)
    if name:
        rule.name = name
    return rule


def add_default_factories(factory_storage: RuleFactoryMixIn) -> None:
    factory_storage.register('dns.dynamic')(dns_create_dynamic_rule)
    factory_storage.register('dns.regex')(dns_create_regex_rule)


__all__ = [
    'RuleFactoryMixIn',
]
