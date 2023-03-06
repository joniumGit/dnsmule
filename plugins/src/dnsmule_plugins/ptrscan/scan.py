from typing import List, Union, Dict

from dns import reversename as reverse_query
from dns.name import Name
from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.rdtypes.IN import A

from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.config import get_logger
from dnsmule.definitions import Record
from dnsmule.rules import Rule


class PTRScan(Rule):
    _backend: DNSPythonBackend

    @staticmethod
    def creator(backend: DNSPythonBackend):
        def ptr_scan(**kwargs):
            be = PTRScan(**kwargs)
            be._backend = backend
            return be

        return ptr_scan

    async def query_records(self, host: Union[str, Name], *types: int) -> Dict[int, List[Rdata]]:
        out = {
            t: []
            for t in types
        }
        for record_type in types:
            async for record in self._backend.dns_query(host, record_type):
                for answer in record.answer:
                    if answer.rdtype == record_type:
                        out[record_type].extend(answer)
        return out

    async def a_to_ptr(self, host: str) -> List[Rdata]:
        """Returns any PTR records for a host
        """
        out = []
        for value in (await self.query_records(host, RdataType.A))[RdataType.A]:
            out.extend(
                (await self.query_records(
                    reverse_query.from_address(value.to_text()),
                    RdataType.PTR,
                ))[RdataType.PTR]
            )
        return out

    async def __call__(self, record: Record):
        og: A = record.data.data['original']
        records = await self.query_records(reverse_query.from_address(og.to_text()), RdataType.PTR)
        if RdataType.PTR in records:
            for r in records[RdataType.PTR]:
                get_logger().info('PTR %s', r.to_text())
            data: dict = record.result().data
            ptrs = [r.to_text() for r in records[RdataType.PTR]]
            data['resolvedPointers'] = ptrs
            ptr_patterns = [
                '-'.join(reversed(og.address.split('.'))),
                '.'.join(reversed(og.address.split('.'))),
                og.address,
                '-'.join(og.address.split('.')),
            ]
            for ptr in ptrs:
                for pattern in ptr_patterns:
                    if pattern in ptr:
                        if ptr.startswith(pattern):
                            _id = ptr.removeprefix(pattern)
                        else:
                            _id = ptr.partition(pattern)[2]
                        record.identify(f'IP:PTR::{self.name.upper()}::{_id.strip(".").upper()}')
                        break


__all__ = [
    'PTRScan',
]
