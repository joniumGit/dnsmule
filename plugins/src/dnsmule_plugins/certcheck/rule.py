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
        certs = []
        for port in self.ports:
            certs.extend(
                certificates.collect_certificates(
                    address,
                    port=port,
                    timeout=self.timeout,
                    prefer_stdlib=self.stdlib,
                )
            )
        domains = set()
        issuers = set()
        for cert in certs:
            issuers.add(cert.issuer)
            domains.update(certificates.resolve_domain_from_certificate(cert))
        domains = process_domains(*domains)
        result = record.result()

        certs = [c.to_json() for c in certs]
        if 'resolvedCertificates' not in result.data:
            result.data['resolvedCertificates'] = certs
        else:
            result.data['resolvedCertificates'].extend(certs)

        if self.callback:
            self._callback(domains)
        return result


__all__ = [
    'CertChecker',
]
