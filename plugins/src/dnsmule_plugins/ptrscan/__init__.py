from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.rules import Rules
from .scan import PTRScan


def plugin_ptr_scan(rules: Rules, backend: DNSPythonBackend):
    rules.register('ip.ptr')(PTRScan.creator(backend))


__all__ = [
    'plugin_ptr_scan'
]
