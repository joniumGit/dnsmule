from typing import Dict, Any, Union, Type, Callable

from .entities import Rule
from .ruletypes import DynamicRule, RegexRule

RuleFactory = Union[Type[Rule], Callable[[...], Rule]]


class RuleFactoryMixIn:
    _factories: Dict[str, RuleFactory]

    def __init__(self):
        self._factories = {}
        self.register(RegexRule)
        self.register(DynamicRule)

    def create(self, type_name: str, definition: Dict[str, Any]) -> Rule:
        """Creates a rule from rule logger
        """
        return self._factories[type_name](**definition)

    def register(self, rule_type: Union[str, Type[Rule]]) -> Union[Callable[[RuleFactory], RuleFactory], Type[Rule]]:
        """Registers a handler for a rule type
        """

        if isinstance(rule_type, type):
            if not issubclass(rule_type, Rule):
                raise TypeError('Not a Rule')
            self._factories[rule_type.id] = rule_type

            return rule_type
        else:
            def decorator(f: RuleFactory) -> RuleFactory:
                self._factories[rule_type] = f
                return f

            return decorator


__all__ = [
    'RuleFactoryMixIn',
    'RuleFactory',
    'Rule',
]
