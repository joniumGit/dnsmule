from typing import Dict

from .entities import Rule, RuleFactory
from .ruletypes import DynamicRule, RegexRule


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


def dns_create_regex_rule(**kwargs) -> RegexRule:
    return RegexRule(**kwargs)


def dns_create_dynamic_rule(**kwargs) -> Rule:
    return DynamicRule(**kwargs)


def add_default_factories(factory_storage: RuleFactoryMixIn) -> None:
    factory_storage.register('dns.dynamic')(dns_create_dynamic_rule)
    factory_storage.register('dns.regex')(dns_create_regex_rule)


__all__ = [
    'RuleFactoryMixIn',
]
