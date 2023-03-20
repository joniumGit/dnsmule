from typing import Callable, Collection, List, Optional

from dnsmule import Rule, Result, Record
from dnsmule.utils import process_domains
from . import certificates


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
        address: str = record.text
        certs = set()
        for port in self.ports:
            certs.update(
                certificates.collect_certificates(
                    address,
                    port=port,
                    timeout=self.timeout,
                    prefer_stdlib=self.stdlib,
                )
            )
        domains = [*process_domains(
            domain
            for cert in certs
            for domain in certificates.resolve_domain_from_certificate(cert)
        )]
        existing = set()
        if 'resolvedCertificates' in record.result.data:
            existing.update(
                certificates.Certificate.from_json(d)
                for d in record.result.data['resolvedCertificates']
            )

        value = []
        value.extend(existing)
        value.extend(c.to_json() for c in certs if c not in existing)
        record.result.data['resolvedCertificates'] = value
        if self.callback:
            self._callback(*domains)
        return record.result


__all__ = [
    'CertChecker',
]
