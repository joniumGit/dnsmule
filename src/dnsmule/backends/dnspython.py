from logging import getLogger
from typing import Dict, Any, Callable, Coroutine, Iterable

from dns.exception import DNSException
from dns.message import Message, make_query
from dns.query import udp_with_fallback, https, quic, udp, tcp, tls
from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.resolver import Resolver
from dns.rrset import RRset

from ..api import Backend, Record, Domain, RRType

LOGGER = 'dnsmule.backends.dnspython'


def default_query(query: Message, *args, **kwargs):
    response, used_tcp = udp_with_fallback(query, *args, **kwargs)
    if used_tcp:
        getLogger(LOGGER).debug('Used TCP fallback query\n%s', query)
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
                name=Domain(result_set.name.to_text(omit_final_dot=True)),
                data=record_data,
            )


class DNSPythonRecord(Record):
    data: Rdata

    @property
    def text(self) -> str:
        return self.data.to_text().removeprefix('"').removesuffix('"')

    def __getattr__(self, item):
        return getattr(self.data, item)


Querier = Callable[..., Coroutine[Any, Any, Message]]


class DNSPythonBackend(Backend):
    """
    DNSPython backend for querying DNS records

    Can be configured with::

        timeout     <int>   Timeout for queries
        querier     <str>   Querier to use (see DNSPython docs for all query types)
                            This is a `dns.query` attribute.
                            Default: tcp with udp fallback
        resolver    <str>   Resolver address to use for DNS queries
                            Default: System default from `Resolver().nameservers[0]`
    """
    type = 'dnspython'

    _SUPPORTED_QUERY_TYPES: Dict[str, Querier] = {
        'tcp': tcp,
        'udp': udp,
        'tls': tls,
        'quic': quic,
        'https': https,
        'default': default_query,
    }

    _querier: Querier

    def __init__(
            self,
            *,
            timeout: float = 2,
            querier: str = 'default',
            resolver: str = None,
    ):
        super(DNSPythonBackend, self).__init__()
        self.timeout = timeout
        self.querier = querier
        self.resolver = resolver
        self._logger = getLogger(LOGGER)
        try:
            self._querier = DNSPythonBackend._SUPPORTED_QUERY_TYPES[self.querier]
        except KeyError:
            raise ValueError(f'Invalid query mode ({self.querier})')
        if not self.resolver:
            self.resolver = Resolver().nameservers[0]
        self._logger.debug('Resolver: %s', self.resolver)

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
            except DNSException as e:
                self._logger.error('%s\n%s', 'Failed query', query, exc_info=e)

    def scan(self, target: Domain, *types: RRType) -> Iterable[Record]:
        for message in self._dns_query(target, *types):
            for record in message_to_record(message):
                yield record
