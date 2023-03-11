from dnsmule import DNSMule
from dnsmule.plugins import Plugin
from .rule import IpRangeChecker


class IPRangesPlugin(Plugin):

    def register(self, mule: DNSMule):
        mule.rules.register('ip.ranges')(IpRangeChecker)


__all__ = [
    'IPRangesPlugin',
]
