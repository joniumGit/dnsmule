from dnsmule.rules import Rules
from .rule import IpRangeChecker


def plugin_ipranges(rules: Rules):
    rules.register('ip.ranges')(IpRangeChecker)


__all__ = [
    'plugin_ipranges',
]
