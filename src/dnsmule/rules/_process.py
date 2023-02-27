from typing import Dict

from dns.message import Message
from dns.name import Name
from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.rrset import RRset

from .entities import Record, Result, Type, Data, Domain
from .rules import Rules


def process_message(rules: Rules, domain: Name, message: Message) -> Dict[RdataType, Result]:
    """Processes a dns message
    """
    rrset: RRset
    rdata: Rdata
    dom = Domain(_wrapped=domain)
    out: Dict[RdataType, Result] = {}
    for rrset in message.answer:
        for rdata in rrset:
            if rdata.rdtype not in out:
                out[rdata.rdtype] = Result(Type(_wrapped=rdata.rdtype), dom)
            out[rdata.rdtype] += rules.process_record(Record(
                type=rdata.rdtype,
                domain=dom,
                data=Data(_wrapped=rdata),
            ))
    return out


__all__ = [
    'process_message',
]
