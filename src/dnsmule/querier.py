import logging
from typing import List, Union, Dict

import dns.reversename as reverse_query
from dns.asyncquery import udp_with_fallback
from dns.message import Message, make_query
from dns.name import Name
from dns.rdatatype import RdataType, is_metatype
from dns.rrset import RRset


class TypeFilter:
    __slots__ = ['type']
    type: int

    def __init__(self, __type: int):
        self.type = __type

    def __call__(self, record: RRset):
        return bool(record.rdtype & self.type)


async def query(host: Union[str, Name], *types: RdataType, resolver: str = '8.8.8.8') -> Message:
    _logger = logging.getLogger('dnsmule')
    for dns_type in types:
        if not is_metatype(dns_type):
            _logger.debug('[%s, %s] Starting query', host, dns_type)
            query = make_query(host, dns_type)
            response, used_tcp = await udp_with_fallback(query, resolver)
            if used_tcp:
                _logger.debug('[%s, %s] Used TCP fallback query', host, dns_type)
            return response


async def query_records(host: Union[str, Name], *types: RdataType, **kwargs) -> Dict[RdataType, List[Name]]:
    out = {
        t: []
        for t in types
    }
    for record_type in types:
        for record in (await query(host, record_type, **kwargs)).answer:
            if record.rdtype == record_type:
                out[record_type].extend(record)
    return out


async def a_to_ptr(host: str, **kwargs) -> List[Name]:
    out = []
    for value in (await query_records(host, RdataType.A, **kwargs))[RdataType.A]:
        out.extend(
            (await query_records(
                reverse_query.from_address(value.to_text()),
                RdataType.PTR,
                **kwargs
            ))[RdataType.PTR]
        )
    return out


def collect_certificate_crptography(host: str, port: int):
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


def collect_certificate(host: str, port: int):
    import ssl
    import socket
    host = socket.gethostbyname(host)
    try:
        cert = collect_certificate_stdlib(host, port)
    except ssl.SSLError:
        cert = None
    if not cert:
        try:
            cert = collect_certificate_crptography(host, port)
        except ImportError:
            pass
    return cert


def resolve_domain_from_certificates(ip: str, port: int = 443) -> List[str]:
    cert = collect_certificate(ip, port=port)
    if cert is not None:
        return [cert['common'], *cert['alts']]
    else:
        return []


def subset_domains(*domains: str) -> List[str]:
    return [*{*(d.lstrip('*.') for d in domains), *('.'.join(d.split('.')[-2:]) for d in domains)}]
