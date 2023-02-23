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
    out: Dict[RdataType, Result] = {t: Result(Type(type=t)) for t in RdataType}
    for rrset in message.answer:
        for rdata in rrset:
            out[rdata.rdtype] += rules.process_record(Record(
                type=rdata.rdtype,
                domain=Domain(name=domain),
                data=Data(data=rdata),
            ))
    return out


__all__ = [
    'process_message',
]
