import ipaddress

from dnsmule import Record, RRType, Domain, Result
from dnsmule.utils import extend_set


class PTRScan:
    type = 'ip.ptr'

    context: dict

    @staticmethod
    def reverse_query(ip: str) -> Domain:
        return Domain(ipaddress.ip_address(ip).reverse_pointer)

    @property
    def mule(self):
        return self.context['mule']

    def __call__(self, record: Record, result: Result):
        address = record.text
        ptr_patterns = [
            '-'.join(reversed(address.split('.'))),
            '.'.join(reversed(address.split('.'))),
            address,
            '-'.join(address.split('.')),
        ]
        ptrs = [
            ptr.text
            for ptr in self.mule.backend.scan(
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
                        result.tags.add(
                            f'IP::PTR'
                            f'::{_id.strip(".").upper()}'
                        )
                        break
            extend_set(result.data, 'resolvedPointers', *ptrs)


__all__ = [
    'PTRScan',
]
