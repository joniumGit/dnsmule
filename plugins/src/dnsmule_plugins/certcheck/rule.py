from typing import Callable, Collection, List

from dnsmule.definitions import Record, Result
from dnsmule.rules import Rule
from dnsmule.utils import process_domains
from . import certificates


class CertChecker(Rule):
    ports: List[int] = [443, 8443]
    timeout: float = 1
    stdlib: bool = False
    callback: bool = False

    _callback: Callable[[Collection[str]], None]

    @staticmethod
    def creator(callback: Callable[[Collection[str]], None]):

        def registerer(**kwargs):
            rule = CertChecker(**kwargs)
            rule._callback = callback
            return rule

        return registerer

    def __call__(self, record: Record) -> Result:
        address: str = record.data.to_text()
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
        domains = set()
        for cert in certs:
            domains.update(certificates.resolve_domain_from_certificate(cert))
        domains = process_domains(*domains)
        existing_result = record.result()
        existing = set()
        if 'resolvedCertificates' in existing_result.data:
            existing.update(certificates.Certificate.from_json(d) for d in existing_result.data['resolvedCertificates'])
        result = Result(existing_result.domain)
        result.data['resolvedCertificates'] = [c.to_json() for c in certs if c not in existing]
        if self.callback:
            self._callback(domains)
        return result


__all__ = [
    'CertChecker',
]
