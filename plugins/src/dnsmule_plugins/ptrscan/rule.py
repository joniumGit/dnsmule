import ipaddress

from dnsmule import DNSMule
from dnsmule.definitions import Record, RRType, Domain, Tag
from dnsmule.rules import Rule
from dnsmule.utils import extend_set


class PTRScan(Rule):
    _id = 'ip.ptr'

    _mule: DNSMule

    @staticmethod
    def creator(mule: DNSMule):
        def ptr_scan(**kwargs):
            be = PTRScan(**kwargs)
            be._mule = mule
            return be

        return ptr_scan

    @staticmethod
    def reverse_query(ip: str) -> Domain:
        return Domain(ipaddress.ip_address(ip).reverse_pointer)

    def __call__(self, record: Record):
        address = record.text
        ptr_patterns = [
            '-'.join(reversed(address.split('.'))),
            '.'.join(reversed(address.split('.'))),
            address,
            '-'.join(address.split('.')),
        ]
        ptrs = [
            ptr.text
            for ptr in self._mule.backend.single(
                self.reverse_query(record.text),
                RRType.PTR,
            )
        ]
        if ptrs:
            for ptr in ptrs:
                for pattern in ptr_patterns:
                    if pattern in ptr:
                        if ptr.startswith(pattern):
                            _id = ptr.removeprefix(pattern)
                        else:
                            _id = ptr.partition(pattern)[2]
                        record.tag(Tag(f'IP::PTR::{self.name.upper()}::{_id.strip(".").upper()}'))
                        break
            extend_set(record.result.data, 'resolvedPointers', ptrs)
        return record.result


__all__ = [
    'PTRScan',
]
