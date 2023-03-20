from os import getenv
from random import choice
from typing import Dict, Any, Callable, Coroutine, Iterable

from dns.exception import DNSException
from dns.message import Message, make_query
from dns.query import udp_with_fallback, https, quic, udp, tcp, tls
from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.rrset import RRset

from .abstract import Backend
from ..definitions import Record, RRType, Domain
from ..logger import get_logger

Querier = Callable[..., Coroutine[Any, Any, Message]]


def default_query(query: Message, *args, **kwargs):
    response, used_tcp = udp_with_fallback(query, *args, **kwargs)
    if used_tcp:
        get_logger().debug('Used TCP fallback query\n%s', query)
    return response


def message_to_record(message: Message) -> Iterable[Record]:
    result_set: RRset
    record_data: Rdata
    from itertools import chain
    for result_set in chain(message.answer, message.additional):
        for record_data in result_set:
            rtype = RRType.from_any(record_data.rdtype)
            yield DNSPythonRecord(
                type=rtype,
                domain=Domain(result_set.name.to_text(omit_final_dot=True)),
                data=record_data,
            )


class DNSPythonRecord(Record):
    data: Rdata

    @property
    def text(self) -> str:
        return self.data.to_text().removeprefix('"').removesuffix('"')

    def __getattr__(self, item):
        return getattr(self.data, item)


class DNSPythonBackend(Backend):
    _SUPPORTED_QUERY_TYPES: Dict[str, Querier] = {
        'tcp': tcp,
        'udp': udp,
        'tls': tls,
        'quic': quic,
        'https': https,
        'default': default_query,
    }

    _DEFAULT_RESOLVER = getenv('DNSMULE_DEFAULT_RESOLVER', choice([
        '208.67.222.222',
        '208.67.220.220',
        '1.1.1.1',
        '1.0.0.1',
        '8.8.8.8',
        '8.8.4.4',
    ]))

    timeout: float = 2
    querier: str = 'default'
    resolver: str = _DEFAULT_RESOLVER

    _querier: Querier

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self._querier = DNSPythonBackend._SUPPORTED_QUERY_TYPES[self.querier]
        except KeyError:
            raise ValueError(f'Invalid query mode ({self.querier})')

    def _dns_query(
            self,
            host: str,
            *types: int,
    ) -> Iterable[Message]:
        for dns_type in types:
            query = make_query(host, RdataType.make(dns_type))
            try:
                response = self._querier(query, self.resolver, timeout=self.timeout)
                yield response
            except DNSException:
                get_logger().error('%s\n%s', 'Failed query', query)

    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        for message in self._dns_query(target, *types):
            for record in message_to_record(message):
                yield record


__all__ = [
    'DNSPythonBackend',
    'DNSPythonRecord',
]
