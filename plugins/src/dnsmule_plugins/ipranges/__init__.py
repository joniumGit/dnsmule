from dnsmule import DNSMule
from dnsmule.plugins import Plugin
from .rule import IpRangeChecker


class IPRangesPlugin(Plugin):
    id = 'ip.ranges'

    def register(self, mule: DNSMule):
        mule.rules.register(IpRangeChecker)


__all__ = [
    'IPRangesPlugin',
]
