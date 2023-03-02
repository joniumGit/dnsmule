from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Certificate:
    common: str
    alts: List[str]


def collect_certificate_cryptography(host: str, port: int):
    try:
        import ssl
        from cryptography.x509 import load_pem_x509_certificates
        from cryptography.x509.oid import NameOID
        from cryptography.x509.oid import ExtensionOID
        from cryptography.x509.extensions import SubjectAlternativeName, DNSName, ExtensionNotFound
        cert = ssl.get_server_certificate((host, port), timeout=.1)
        cert = load_pem_x509_certificates(cert.encode())[0]
        try:
            alts = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
            alts = [o for o in alts.get_values_for_type(DNSName)]
        except ExtensionNotFound:
            alts = []
        cert = {
            'common': cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
            'alts': alts
        }
        return cert
    except IndexError:
        return None
    except ImportError:
        return None
    except Exception as e:
        import logging
        logging.getLogger('dnsmule').warning('Failed connect to %s:%s (%s)', host, port, type(e).__name__)


def massage_certificate_stdlib(certificate):
    if certificate is not None and len(certificate) != 0:
        _alts = []
        _commonName = None
        for field_set in certificate['subject']:
            for field in field_set:
                _key, _value = field
                if _key == 'commonName':
                    _commonName = _value
                    break
            if _commonName is not None:
                break
        for alt_names in certificate.get('subjectAltName', ()):
            _type, _name = alt_names
            if _type == 'DNS':
                _alts.append(_name)
        return {
            'common': _commonName,
            'alts': _alts
        }


def collect_certificate_stdlib(host: str, port: int):
    try:
        import ssl
        import socket
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_flags = ssl.CERT_REQUIRED
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as raw_socket:
            raw_socket.settimeout(.1)
            with ctx.wrap_socket(raw_socket, do_handshake_on_connect=True) as s:
                s.connect((host, port))
                return massage_certificate_stdlib(s.getpeercert(binary_form=False))
    except TimeoutError:
        import logging
        logging.getLogger('dnsmule').warning('Failed connect to %s:%s (TimeoutError)', host, port)


def collect_certificate(host: str, port: int) -> Optional[Certificate]:
    import ssl
    import socket
    host = socket.gethostbyname(host)
    try:
        cert = collect_certificate_stdlib(host, port)
    except ssl.SSLError:
        cert = None
    if not cert:
        cert = collect_certificate_cryptography(host, port)
    return Certificate(**cert) if cert else None


__all__ = [
    'collect_certificate',
    'Certificate',
]
