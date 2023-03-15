from dnsmule import DNSMule
from dnsmule.plugins import Plugin
from .rule import PTRScan


class PTRScanPlugin(Plugin):

    def register(self, mule: DNSMule):
        mule.rules.register('ip.ptr')(PTRScan.creator(mule))


__all__ = [
    'PTRScanPlugin'
]
