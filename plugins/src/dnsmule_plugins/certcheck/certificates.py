import datetime
import sys
from dataclasses import dataclass
from typing import List, Optional

from dnsmule.config import get_logger


@dataclass
class Certificate:
    version: str
    common: str
    alts: List[str]
    issuer: str
    valid_until: datetime.datetime
    valid_from: datetime.datetime

    def to_json(self):
        from dataclasses import asdict
        data = asdict(self)
        return {
            'valid_until': data.pop('valid_until').isoformat(),
            'valid_from': data.pop('valid_from').isoformat(),
            **data,
        }


def collect_certificate_cryptography(host: str, port: int, timeout: float):
    import ssl
    try:
        from cryptography.x509 import load_pem_x509_certificates
        from cryptography.x509.oid import NameOID
        from cryptography.x509.oid import ExtensionOID
        from cryptography.x509.extensions import SubjectAlternativeName, DNSName, ExtensionNotFound
        cert = ssl.get_server_certificate((host, port), timeout=timeout)
        cert = load_pem_x509_certificates(cert.encode())[0]
        try:
            alts = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
            alts = [o for o in alts.get_values_for_type(DNSName)]
        except ExtensionNotFound:
            alts = []
        cert = {
            'common': cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
            'alts': alts,
            'issuer': cert.issuer.rfc4514_string(),
            'valid_until': cert.not_valid_after,
            'valid_from': cert.not_valid_before,
            'version': cert.version.name,
        }
        return cert
    except ImportError:
        pass
    except Exception as e:
        get_logger().warning('CERTS-CRYPTOGRAPHY: Failed to get cert for %s:%s (%s)', host, port, type(e).__name__)


def issuer_str(issuer):
    mapper = {
        'commonName': 'CN',
        'organizationName': 'O',
        'countryName': 'C',
    }
    key: str
    value: str
    return ','.join(
        f'{mapper[key]}=' + value.replace(',', r'\,').replace('=', r'\=')
        for key, value in map(lambda t: t[0], issuer[::-1])
    )


def massage_certificate_stdlib(certificate):
    if certificate:
        import ssl
        return {
            'common': next(
                value
                for entry in certificate['subject']
                for field, value in entry
                if field == 'commonName'
            ),
            'alts': [
                alt
                for _type, alt in certificate.get('subjectAltName', [])
                if _type == 'DNS'
            ],
            'issuer': issuer_str(certificate['issuer']),
            'valid_until': datetime.datetime.utcfromtimestamp(
                ssl.cert_time_to_seconds(certificate['notAfter']),
            ),
            'valid_from': datetime.datetime.utcfromtimestamp(
                ssl.cert_time_to_seconds(certificate['notBefore']),
            ),
            'version': 'v%d' % certificate.get('version'),
        }


def collect_certificate_stdlib(host: str, port: int, timeout: float):
    import ssl
    import socket
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as raw_socket:
            raw_socket.settimeout(timeout)
            with ctx.wrap_socket(raw_socket, do_handshake_on_connect=True) as s:
                s.connect((host, port))
                return massage_certificate_stdlib(s.getpeercert(binary_form=False))
    except Exception as e:
        get_logger().warning('CERTS-STDLIB: Failed to get cert for %s:%s (%s)', host, port, type(e).__name__)


def collect_certificate(
        host: str,
        port: int,
        timeout: float = 1.,
        prefer_stdlib: bool = True,
) -> Optional[Certificate]:
    import socket
    try:
        host = socket.gethostbyname(host)
    except socket.gaierror:
        return None
    if prefer_stdlib:
        cert = collect_certificate_stdlib(host, port, timeout)
    else:
        try:
            import cryptography
        except ImportError:
            get_logger().error('Cryptography not installed')
            raise
        cert = None
    if not cert:
        cert = collect_certificate_cryptography(host, port, timeout)
    return Certificate(**cert) if cert else None


def resolve_domain_from_certificate(cert: Certificate) -> List[str]:
    """Returns all names from a certificate retrieved from an ip-address

    Common name is the first one if available followed by any alternative names
    """
    if cert is not None:
        return [cert.common, *cert.alts]
    else:
        return []


__all__ = [
    'collect_certificate',
    'Certificate',
    'resolve_domain_from_certificate',
]

if __name__ == '__main__':  # pragma: no cover
    import json
    import dataclasses

    c1 = collect_certificate(sys.argv[1], 443)
    c2 = collect_certificate(sys.argv[1], 443, prefer_stdlib=False)

    print(json.dumps(dataclasses.asdict(c1), indent=4, default=str))
    print(json.dumps(dataclasses.asdict(c2), indent=4, default=str))
