from typing import Callable, Collection, List, Optional

from dnsmule import Rule, Result, Record
from dnsmule.utils import extend_set
from . import certificates
from .domains import process_domains
from .adapter import load_result, save_result


class CertChecker(Rule):
    id = 'ip.certs'

    ports: List[int] = [443, 8443]
    timeout: float = 1
    stdlib: bool = False
    callback: bool = False

    _callback: Callable[[str, ...], None]

    @staticmethod
    def creator(callback: Optional[Callable[[Collection[str]], None]]):
        def registerer(**kwargs):
            rule = CertChecker(**kwargs)
            rule._callback = callback
            return rule

        return registerer

    def __call__(self, record: Record) -> Result:
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
            load_result(record.result)
            extend_set(record.result.data, 'resolvedCertificates', certs)
            save_result(record.result)
            if self.callback:
                domains = [*process_domains(
                    domain
                    for cert in certs
                    for domain in certificates.resolve_domain_from_certificate(cert)
                    if domain != record.domain
                )]
                self._callback(*domains)
        return record.result


__all__ = [
    'CertChecker',
]
