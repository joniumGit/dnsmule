from typing import Union, Dict, AsyncGenerator, Any, Callable, Coroutine, Generator

from dns.asyncquery import udp_with_fallback, https, quic, udp, tcp, tls
from dns.exception import Timeout
from dns.message import Message, make_query
from dns.name import Name
from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.rrset import RRset

from .abstract import Backend
from ..config import get_logger, defaults
from ..definitions import Record, RRType, Data, Domain

_Querier = Callable[..., Coroutine[Any, Any, Message]]


async def _default_query(query: Message, *args, **kwargs):
    response, used_tcp = await udp_with_fallback(query, *args, **kwargs)
    if used_tcp:
        get_logger().debug('Used TCP fallback query\n%s', query)
    return response


class DNSPythonBackend(Backend):
    _MODE_MAPPING: Dict[str, _Querier] = {
        'tcp': tcp,
        'udp': udp,
        'tls': tls,
        'http': https,
        'quic': quic,
        'default': _default_query,
    }

    timeout: float = 2
    querier: str = 'default'
    resolver: str = defaults.DEFAULT_RESOLVER
    _querier: _Querier

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self._querier = DNSPythonBackend._MODE_MAPPING[self.querier]
        except KeyError:
            raise ValueError(f'Invalid query mode ({self.querier})')
        self.enable_data_extension()

    async def dns_query(
            self,
            host: Union[str, Name],
            *types: int,
    ) -> AsyncGenerator[Any, Message]:
        for dns_type in types:
            dns_type = RdataType.make(dns_type)
            query = make_query(host, dns_type)
            get_logger().debug('%s\n%s', 'Starting query', query)
            try:
                response = await self._querier(query, self.resolver, timeout=self.timeout)
                yield response
            except Timeout:
                get_logger().error('%s\n%s', 'Timed out query', query)

    @staticmethod
    def _process_message(
            domain: Domain,
            message: Message,
    ) -> Generator[Record, Any, Any]:
        """Processes a dns message
        """
        result_set: RRset
        record_data: Rdata
        for result_set in message.answer:
            for record_data in result_set:
                rtype = RRType.from_any(record_data.rdtype)
                yield Record(
                    type=rtype,
                    domain=domain,
                    data=Data(
                        type=rtype,
                        value=record_data.to_text().removesuffix('"').removeprefix('"'),
                        original=record_data,
                    ),
                )

    async def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        async for message in self.dns_query(target.name, *iter(RdataType.make(t) for t in types)):
            for record in self._process_message(target, message):
                yield record

    @staticmethod
    def enable_data_extension():

        def _getattr(self: Data, item: str):
            if 'original' in self.data:
                return getattr(self.data['original'], item)

        Data.register_adapter(_getattr)


__all__ = [
    'DNSPythonBackend',
]
