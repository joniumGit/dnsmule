from dnsmule import DNSMule
from dnsmule.config import get_logger
from dnsmule.plugins import Plugin


class CertCheckPlugin(Plugin):
    callback: bool

    def register(self, mule: DNSMule):
        try:
            from .rule import CertChecker
            mule.rules.register('ip.certs')(CertChecker.creator(
                lambda results: mule.store_domains(*results)
                if self.callback else
                None
            ))
        except ImportError as e:
            get_logger().exception('Failed to add CertCheckPlugin', exc_info=e)


__all__ = [
    'CertCheckPlugin',
]
