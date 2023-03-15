import ipaddress

from dnsmule import DNSMule
from dnsmule.definitions import Record, Result, RRType, Domain
from dnsmule.rules import Rule


class PTRScan(Rule):
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

    async def __call__(self, record: Record) -> Result:
        result = Result(domain=record.domain)
        address = record.data.to_text()
        ptr_patterns = [
            '-'.join(reversed(address.split('.'))),
            '.'.join(reversed(address.split('.'))),
            address,
            '-'.join(address.split('.')),
        ]
        ptrs = [
            ptr.data.to_text()
            async for ptr in self._mule.backend.run_single(
                self.reverse_query(record.data.to_text()),
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
                        result.tags.add(f'IP::PTR::{self.name.upper()}::{_id.strip(".").upper()}')
                        break
            existing_result = record.result()
            existing = set()
            if 'resolvedPointers' in existing_result.data:
                existing.update(existing_result.data['resolvedPointers'])
            result.data['resolvedPointers'] = [p for p in ptrs if p not in existing]
        return result


__all__ = [
    'PTRScan',
]
