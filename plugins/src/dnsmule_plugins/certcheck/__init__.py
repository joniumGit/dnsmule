from typing import Optional, Callable, Collection

from dnsmule import DNSMule, Domain, Plugin
from .adapter import load_result, save_result
from .rule import CertChecker


class CertCheckPlugin(Plugin):
    id = 'ip.certs'
    callback: bool = False

    def get_callback(self, mule: DNSMule) -> Optional[Callable[[Collection[Domain]], None]]:
        if self.callback:
            return mule.scan

    def register(self, mule: DNSMule):
        mule.rules.register(CertChecker.id)(CertChecker.creator(self.get_callback(mule)))


__all__ = [
    'CertCheckPlugin',
]
