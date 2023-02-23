from typing import List, Union, Dict

from dns.asyncquery import udp_with_fallback
from dns.message import Message, make_query
from dns.name import Name
from dns.rdata import Rdata
from dns.rdatatype import RdataType, is_metatype

from ..config import defaults, get_logger


async def query(host: Union[str, Name], *types: RdataType, resolver: str = defaults.DEFAULT_RESOLVER) -> Message:
    for dns_type in types:
        if not is_metatype(dns_type):
            get_logger().debug('[%s, %s] Starting query', host, dns_type)
            _query = make_query(host, dns_type)
            response, used_tcp = await udp_with_fallback(_query, resolver)
            if used_tcp:
                get_logger().debug('[%s, %s] Used TCP fallback query', host, dns_type)
            return response


async def query_records(host: Union[str, Name], *types: RdataType, **kwargs) -> Dict[RdataType, List[Rdata]]:
    out = {
        t: []
        for t in types
    }
    for record_type in types:
        for record in (await query(host, record_type, **kwargs)).answer:
            if record.rdtype == record_type:
                out[record_type].extend(record)
    return out


__all__ = [
    'query_records',
]
