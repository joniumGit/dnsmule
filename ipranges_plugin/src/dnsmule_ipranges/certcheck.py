from typing import Callable, Collection, List

from dnsmule.definitions import Record
from dnsmule.rules import Rules, Rule
from dnsmule.utils import process_domains
from . import certificates


class CertChecker(Rule):
    ports: List[int]
    timeout: float
    stdlib: bool
    _callback: Callable[[Collection[str]], None]

    @staticmethod
    def creator(callback: Callable[[Collection[str]], None]):

        def registerer(**kwargs):
            rule = CertChecker(**kwargs)
            rule._callback = callback
            return rule

        return registerer

    def __call__(self, record: Record) -> None:
        address: str = record.data.to_text()
        certs = []
        for port in self.ports:
            cert = certificates.collect_certificate(
                address,
                port=port,
                timeout=self.timeout,
                prefer_stdlib=self.stdlib,
            )
            if cert:
                certs.append(cert)
        domains = []
        for cert in certs:
            domains.extend(certificates.resolve_domain_from_certificate(cert))
        domains = process_domains(*domains)
        result = record.result()
        result.data['resolvedDomains'] = domains
        self._callback(domains)
        return result


def add_cert_checker(rules: Rules, datasource_callback: Callable[[Collection[str]], None]):
    rules.register('ip.certs')(CertChecker.creator(datasource_callback))


__all__ = [
    'add_cert_checker',
]
