from typing import Callable

from dns.rdtypes import IN, CH, ANY
from dns.rdtypes.ANY import TXT, CNAME, MX, NS
from dns.rdtypes.IN import A, AAAA

from .data import Record, Result

RULE_TYPE = Callable[[Record], Result]

__all__ = [
    'RULE_TYPE',
    'Record',
    'Result',
    # General
    'IN',
    'CH',
    'ANY',
    # Convenience
    'TXT',
    'CNAME',
    'MX',
    'NS',
    'A',
    'AAAA',
]
