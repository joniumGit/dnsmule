from functools import partial
from typing import Dict, List

from .entities import Type
from .rules import Rules
from .ruletypes import DynamicRule


def load_and_append_rule(rules: Rules, rule_definition: Dict):
    """Creates a rule from rule definition

    Initializes any dynamic rules created and passes the add_rule callback to them
    """
    rule_record_type = Type.from_any(rule_definition.pop('record'))
    rule = rules.create_rule(rule_definition)
    if isinstance(rule, DynamicRule):
        rule.init(partial(load_and_append_rule, factory_provider=rules))
    rules.add_rule(rule_record_type, rule)


def load_rules_from_config(config: List[Dict[str, Dict]], rules: Rules = None) -> Rules:
    """Loads rules from the rules element in rules.yml

    Provider rules in case of non-default handlers.
    """
    rules = Rules() if rules is None else rules
    for rule_definition in config:
        name = next(iter(rule_definition.keys()))
        if 'name' not in rule_definition:
            rule_definition['name'] = name
        load_and_append_rule(rules, rule_definition)
    return rules


def load_config(file: str, rules: Rules = None) -> Rules:
    """Loads rules from yaml config
    """
    import yaml
    with open(file, 'r') as f:
        document = yaml.safe_load(f)
        return load_rules_from_config(document['rules'], rules=rules)


__all__ = [
    'DynamicRule',
    'load_config',
]
