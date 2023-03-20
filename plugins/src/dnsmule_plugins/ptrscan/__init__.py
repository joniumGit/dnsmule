from dnsmule import DNSMule
from dnsmule.plugins import Plugin
from .rule import PTRScan


class PTRScanPlugin(Plugin):
    _id = 'plugin.ip.ptr'

    def register(self, mule: DNSMule):
        mule.rules.register(PTRScan.id)(PTRScan.creator(mule))


__all__ = [
    'PTRScanPlugin'
]
