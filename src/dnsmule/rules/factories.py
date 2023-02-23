from typing import List, Union

from .dynamic import DynamicRule
from .types import RULE_TYPE, Record
from .rules import Rules


def dns_create_regex_rule(
        name: str,
        pattern: str,
        identification: str = None,
        flags: List[str] = None,
        attribute: str = 'to_text',
        group: Union[int, str] = None,
) -> RULE_TYPE:
    import re
    import functools
    import operator

    all_flags = {k.lower(): v for k, v in re.RegexFlag.__members__.items()}
    flags = functools.reduce(
        operator.or_,
        (all_flags[flag.lower()] for flag in flags if flag in all_flags),
    )
    p = re.compile(pattern, flags=flags)

    def regex_rule(record: Record):
        m = p.search(str(getattr(record.data, attribute)))
        if m:
            _id = identification if group is None else m.group(group)
            return record.identify(f'DNS::REGEX::{_id.upper()}')

    regex_rule.__name__ = name
    regex_rule.__type__ = 'dns.regex'

    return regex_rule


def dns_create_dynamic_rule(
        name: str,
        code: str,
):
    return DynamicRule(name, code)


def add_default(rules: Rules) -> None:
    rules.register('dns.dynamic', dynamic=True)(dns_create_dynamic_rule)
    rules.register('dns.regex')(dns_create_regex_rule)


__all__ = [
    'add_default',
]
