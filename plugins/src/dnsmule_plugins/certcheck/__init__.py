from typing import Optional, Callable, Collection

from dnsmule import DNSMule, Domain, Plugin
from dnsmule.adapter import patch_storage, Adapter
from .adapter import load_result, save_result
from .rule import CertChecker


class CertCheckPlugin(Plugin):
    id = 'ip.certs'
    callback: bool = False

    def get_callback(self, mule: DNSMule) -> Optional[Callable[[Collection[Domain]], None]]:
        if self.callback:
            return mule.scan

    def register(self, mule: DNSMule):
        patch_storage(mule.storage, Adapter(loader=load_result, saver=save_result))
        mule.rules.register(CertChecker.id)(CertChecker.creator(self.get_callback(mule)))


__all__ = [
    'CertCheckPlugin',
]
