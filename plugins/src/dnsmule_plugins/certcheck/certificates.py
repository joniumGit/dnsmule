import datetime
import socket
from dataclasses import dataclass
from typing import List, Optional, Tuple

from dnsmule.config import get_logger


@dataclass(frozen=True, unsafe_hash=True, eq=True)
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


@dataclass
class Address:
    family: socket.AddressFamily
    tuple: Tuple


def collect_certificate_cryptography(address: Address, timeout: float):
    import ssl
    try:
        from cryptography.x509 import load_pem_x509_certificates
        from cryptography.x509.oid import NameOID
        from cryptography.x509.oid import ExtensionOID
        from cryptography.x509.extensions import SubjectAlternativeName, DNSName, ExtensionNotFound
        cert = ssl.get_server_certificate(address.tuple[0:2], timeout=timeout)
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
        get_logger().warning(
            'CERTS-CRYPTOGRAPHY: Failed to get cert for %s:%s (%s)',
            *address.tuple[0:2],
            type(e).__name__,
        )


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


def collect_certificate_stdlib(address: Address, timeout: float):
    import ssl
    import socket
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        with socket.socket(address.family, socket.SOCK_STREAM) as raw_socket:
            raw_socket.settimeout(timeout)
            with ctx.wrap_socket(raw_socket, do_handshake_on_connect=True) as s:
                s.connect(address.tuple)
                return massage_certificate_stdlib(s.getpeercert(binary_form=False))
    except Exception as e:
        get_logger().warning(
            'CERTS-STDLIB: Failed to get cert for %s:%s (%s)',
            *address.tuple[0:2],
            type(e).__name__,
        )


def collect_certificate(
        address: Address,
        timeout: float = 1.,
        prefer_stdlib: bool = True,
) -> Optional[Certificate]:
    if prefer_stdlib:
        cert = collect_certificate_stdlib(address, timeout)
    else:
        try:
            import cryptography
        except ImportError:
            get_logger().error('Cryptography not installed')
            raise
        cert = None
    if not cert:
        cert = collect_certificate_cryptography(address, timeout)
    return Certificate(**cert) if cert else None


def collect_certificates(host: str, port: int, **kwargs) -> List[Certificate]:
    import socket
    out = []
    try:
        for family, _, _, _, info in socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP):
            cert = collect_certificate(Address(family=family, tuple=info), **kwargs)
            if cert:
                out.append(cert)
    except socket.error:
        pass
    return out


def resolve_domain_from_certificate(cert: Certificate) -> List[str]:
    """Returns all names from a certificate retrieved from an ip-address

    Common name is the first one if available followed by any alternative names
    """
    if cert is not None:
        return [cert.common, *cert.alts]
    else:
        return []


__all__ = [
    'collect_certificates',
    'Certificate',
    'resolve_domain_from_certificate',
]
