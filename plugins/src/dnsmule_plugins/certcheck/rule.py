from typing import List

from dnsmule import Result, Record
from dnsmule.utils import extend_set
from . import certificates
from .adapter import load_result, save_result


class CertChecker:
    type = 'ip.certs'

    def __init__(
            self,
            ports: List[int] = None,
            timeout: float = 1,
            stdlib: bool = False,
    ):
        self.ports = [443, 8443] if ports is None else ports
        self.timeout = timeout
        self.stdlib = stdlib

    def __call__(self, record: Record, result: Result):
        certs = {
            cert
            for port in self.ports
            for cert in certificates.collect_certificates(
                record.text,
                port=port,
                timeout=self.timeout,
                prefer_stdlib=self.stdlib,
            )
        }
        if certs:
            load_result(result)
            extend_set(result.data, 'resolvedCertificates', *certs)
            save_result(result)


__all__ = [
    'CertChecker',
]
