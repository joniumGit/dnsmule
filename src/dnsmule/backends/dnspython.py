from typing import Union, Dict, Optional, AsyncGenerator, Any, List

import dns.reversename as reverse_query
from dns.asyncquery import udp_with_fallback
from dns.exception import Timeout
from dns.message import Message, make_query
from dns.name import Name
from dns.rdata import Rdata
from dns.rdatatype import RdataType, is_metatype
from dns.rrset import RRset

from .abstract import Backend
from ..config import defaults, get_logger
from ..definitions import Record, Result, RRType, Data, Domain


def process_message(domain: Domain, message: Message) -> Dict[RRType, Result]:
    """Processes a dns message
    """
    rrset: RRset
    rdata: Rdata
    for rrset in message.answer:
        for rdata in rrset:
            rtype = RRType.from_any(rdata.rdtype)
            yield Record(
                type=rtype,
                domain=domain,
                data=Data(
                    type=rtype,
                    value=rdata.to_text().removesuffix('"').removeprefix('"'),
                    original=rdata,
                ),
            )


def _getattr(self: Data, item: str):
    if 'original' in self.data:
        return getattr(self.data['original'], item)


Data.register_adapter(_getattr)


async def query(
        host: Union[str, Name],
        *types: int,
        resolver: str = defaults.DEFAULT_RESOLVER,
) -> Optional[Message]:
    for dns_type in types:
        dns_type = RdataType.make(dns_type)
        if not is_metatype(dns_type):
            get_logger().debug('[%s, %s] Starting query', host, dns_type)
            _query = make_query(host, dns_type)
            try:
                response, used_tcp = await udp_with_fallback(_query, resolver, timeout=2)
                if used_tcp:
                    get_logger().debug('[%s, %s] Used TCP fallback query', host, dns_type)
                return response
            except Timeout:
                get_logger().error('[%s, %s] Timed out query', host, dns_type)


async def query_records(host: Union[str, Name], *types: int, **kwargs) -> Dict[int, List[Rdata]]:
    out = {
        t: []
        for t in types
    }
    for record_type in types:
        for record in (await query(host, record_type, **kwargs)).answer:
            if record.rdtype == record_type:
                out[record_type].extend(record)
    return out


class DNSPythonBackend(Backend):

    async def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        message = await query(target.name, *iter(RdataType.make(t) for t in types))
        if message:
            for record in process_message(target, message):
                yield record


async def a_to_ptr(host: str, **kwargs) -> List[Rdata]:
    """Returns any PTR records for a host
    """
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


__all__ = [
    'DNSPythonBackend',
    'query_records',
    'a_to_ptr',
    'query',
]
