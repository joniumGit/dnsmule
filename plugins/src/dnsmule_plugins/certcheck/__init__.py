from dnsmule import DNSMule
from dnsmule.plugins import Plugin

from .rule import CertChecker


class CertCheckPlugin(Plugin):
    callback: bool = False

    def get_callback(self, mule: DNSMule):
        if self.callback:
            return mule.store_domains

    def register(self, mule: DNSMule):
        mule.rules.register('ip.certs')(CertChecker.creator(self.get_callback(mule)))


__all__ = [
    'CertCheckPlugin',
]
