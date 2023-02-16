from typing import List

import dns.reversename as reverse_query
from dns.name import Name
from dns.rdatatype import RdataType

from .queries import query_records


async def a_to_ptr(host: str, **kwargs) -> List[Name]:
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
    'a_to_ptr',
]
