from functools import partial
from typing import Dict

from .entities import DynamicRule, Type
from .rules import Rules


def load_and_append_rule(rules: Rules, rule_definition: Dict):
    """Creates a rule from rule definition
    """
    rule_record_type = Type.from_text(rule_definition.pop('record'))
    rule = rules.create_rule(rule_definition)
    if isinstance(rule, DynamicRule):
        rule.init(partial(load_and_append_rule, factory_provider=rules))
    rules.add_rule(rule_record_type, rule)


def load_rules_from_config(config: Dict[str, Dict], rules: Rules = None) -> Rules:
    """Loads rules from the rules element in rules.yml

    Provider rules in case of non-default handlers.
    """
    rules = Rules() if rules is None else rules
    for name, rule_definition in config.items():
        if 'name' not in rule_definition:
            rule_definition['name'] = name
        load_and_append_rule(rules, rule_definition)
    return rules


__all__ = [
    'load_rules_from_config',
    'load_and_append_rule',
]
