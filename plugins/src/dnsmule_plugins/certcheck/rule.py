from typing import Callable, Collection, List, Optional

from dnsmule import Rule, Result, Record
from dnsmule.utils import extend_set, transform_set
from . import certificates
from .domains import process_domains


class CertChecker(Rule):
    _id = 'ip.certs'

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
            transform_set(record.result.data, 'resolvedCertificates', certificates.Certificate.from_json)
            extend_set(record.result.data, 'resolvedCertificates', certs)
            transform_set(record.result.data, 'resolvedCertificates', certificates.Certificate.to_json)
            if self.callback:
                domains = [*process_domains(
                    domain
                    for cert in certs
                    for domain in certificates.resolve_domain_from_certificate(cert)
                )]
                self._callback(*domains)
        return record.result


__all__ = [
    'CertChecker',
]
