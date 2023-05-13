from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address, ip_address, ip_network
from typing import Union


@dataclass
class IPvXRange:
    address: Union[IPv4Network, IPv6Network]
    region: str
    service: str

    def __contains__(self, item: Union[str, IPv4Address, IPv6Address]):
        try:
            if isinstance(item, str):
                item = ip_address(item)
            return item in self.address
        except ValueError:
            return False

    @staticmethod
    def create(address: str, service: str, region: str) -> 'IPvXRange':
        return IPvXRange(
            address=ip_network(address, strict=False),
            region=region,
            service=service,
        )


__all__ = [
    'IPvXRange',
]
