from typing import List

from ..rules import rule, Record


def create_regex_rule(
        __rtype__: str,
        name: str,
        pattern: str,
        identification: str,
        flags: List[str] = None,
        attribute: str = 'to_text',
):
    import re
    import functools
    import operator

    all_flags = {**re.RegexFlag.__members__}
    flags = functools.reduce(
        operator.or_,
        (all_flags[flag] for flag in flags if flag in all_flags),
    )
    p = re.compile(pattern, flags=flags)

    def regex_rule(record: Record):
        if p.search(str(getattr(record.data, attribute))):
            return record.identify(f'DNS::REGEX::{identification}')

    regex_rule.__name__ = name

    getattr(rule, __rtype__)(regex_rule)


MAPPING = {
    'dns.regex': create_regex_rule
}


def create_rule(rule_type: str, record_type: str, **options) -> None:
    return MAPPING[rule_type](__rtype__=record_type, **options)
