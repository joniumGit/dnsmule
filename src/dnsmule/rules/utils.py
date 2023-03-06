from functools import partial
from pathlib import Path
from typing import Dict, List, Any, Union

from .rules import Rules
from .ruletypes import DynamicRule
from ..definitions import RRType


def load_and_append_rule(rules: Rules, rule_definition: Dict):
    """Creates a rule from rule definition

    Initializes any dynamic rules created and passes the add_rule callback to them
    """
    rule_record_type = RRType.from_any(rule_definition.pop('record'))
    rule = rules.create_rule(rule_definition)
    if isinstance(rule, DynamicRule):
        rule.init(partial(load_and_append_rule, rules))
    rules.add_rule(rule_record_type, rule)


def load_rules(config: List[Dict[str, Any]], rules: Rules = None) -> Rules:
    """Loads rules from the rules element in rules.yml

    Provider rules in case of non-default handlers.
    """
    rules = Rules() if rules is None else rules
    for rule_definition in config:
        name = next(iter(rule_definition.keys()))
        if 'name' not in rule_definition:
            rule_definition['name'] = name
        if rule_definition[name] is None:
            rule_definition.pop(name)
        load_and_append_rule(rules, rule_definition)
    return rules


def load_config(file: Union[str, Path], rules: Rules = None) -> Rules:
    """Loads rules from yaml config
    """
    import yaml
    with open(file, 'r') as f:
        document = yaml.safe_load(f)
        return load_rules(document['rules'], rules=rules)


__all__ = [
    'DynamicRule',
    'load_config',
    'load_rules',
]
