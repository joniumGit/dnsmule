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
    _logger = logging.getLogger('dnsmule.query')
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


def collect_names_from_certificate(certificate) -> List[str]:
    if certificate is not None:
        results = set()
        _commonName = None
        for field_set in certificate['subject']:
            for field in field_set:
                _key, _value = field
                if _key == 'commonName':
                    _commonName = _value
                    break
            if _commonName is not None:
                break
        results.add(_commonName)
        for alt_names in certificate.get('subjectAltName', ()):
            _type, _name = alt_names
            results.add(_name)
        return [*results]
    else:
        return []


def resolve_domain_from_certificates(ip: str, port: int = 443) -> List[str]:
    try:
        import ssl
        import socket

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as raw_socket:
            raw_socket.settimeout(.1)
            with ctx.wrap_socket(raw_socket, do_handshake_on_connect=True) as s:
                s.connect((ip, port))
                cert = s.getpeercert(binary_form=False)
    except TimeoutError:
        pass
    else:
        if cert is not None:
            return collect_names_from_certificate(cert)
    return []
