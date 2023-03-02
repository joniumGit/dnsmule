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


def add_default_factories(factory_storage: RuleFactoryMixIn) -> None:
    factory_storage.register('dns.dynamic')(DynamicRule)
    factory_storage.register('dns.regex')(RegexRule)


__all__ = [
    'RuleFactoryMixIn',
]
