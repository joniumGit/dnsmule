from dnsmule import DNSMule
from dnsmule.config import get_logger
from dnsmule.plugins import Plugin
from .rule import PTRScan


class PTRScanPlugin(Plugin):

    def register(self, mule: DNSMule):
        if mule.backend_type == 'DNSPythonBackend':
            from dnsmule.backends.dnspython import DNSPythonBackend
            from typing import cast
            mule.rules.register('ip.ptr')(PTRScan.creator(cast(DNSPythonBackend, mule.backend)))
        else:
            get_logger().error('Failed to add PTRScanPlugin: Backend not suitable')


__all__ = [
    'PTRScanPlugin'
]
