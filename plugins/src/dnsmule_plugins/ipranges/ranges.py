import ipaddress
import json
from dataclasses import dataclass
from html.parser import HTMLParser
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address
from typing import Set, Union, List
from urllib.request import urlopen


@dataclass
class IPvXRange:
    address: Union[IPv4Network, IPv6Network]
    region: str
    service: str

    def __contains__(self, item: Union[str, IPv4Address, IPv6Address]):
        try:
            if isinstance(item, str):
                item = ipaddress.ip_address(item)
            return item in self.address
        except ValueError:
            return False


class MicrosoftDownloadGrabber(HTMLParser):
    json_url: str = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'a':
            attrs = {k: v for k, v in attrs}
            if attrs.get('href', '').startswith('https://download.microsoft.com'):
                if self.json_url is None:
                    self.json_url = attrs['href']


def fetch_google_ip_ranges_goog() -> Set[IPv4Network]:
    host = 'https://www.gstatic.com/ipranges/goog.json'

    with urlopen(host) as f:
        data = json.load(f)

    return {
        IPv4Network(e['ipv4Prefix'])
        if 'ipv4Prefix' in e
        else IPv6Network(e['ipv6Prefix'])
        for e in data['prefixes']
    }


def fetch_google_ip_ranges_cloud() -> List[IPvXRange]:
    host = 'https://www.gstatic.com/ipranges/cloud.json'

    with urlopen(host) as f:
        data = json.load(f)

    return [
        IPvXRange(
            address=IPv4Network(e['ipv4Prefix']) if 'ipv4Prefix' in e else IPv6Network(e['ipv6Prefix']),
            region=e['scope'],
            service=f'GOOGLE::{e["service"] or "GENERIC"}'.upper(),
        )
        for e in data['prefixes']
    ]


def fetch_google_ip_ranges():
    ranges_cloud = fetch_google_ip_ranges_cloud()
    ranges_goog = fetch_google_ip_ranges_goog()
    return [
        e
        for e in ranges_cloud
        if e.address not in ranges_goog
    ]


def fetch_amazon_ip_ranges() -> List[IPvXRange]:
    host = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

    with urlopen(host) as f:
        data = json.load(f)

    return [
        *(
            IPvXRange(
                address=IPv4Network(e['ip_prefix']),
                region=e['region'],
                service=f'AMAZON::{e["service"]}'.upper(),
            )
            for e in data['prefixes']
        ),
        *(
            IPvXRange(
                address=IPv6Network(e['ipv6_prefix']),
                region=e['region'],
                service=f'AMAZON::{e["service"] or "GENERIC"}'.upper(),
            )
            for e in data['ipv6_prefixes']
        )
    ]


def fetch_microsoft_ip_ranges() -> List[IPvXRange]:
    host = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
    p = MicrosoftDownloadGrabber()
    with urlopen(host) as f:
        p.feed(f.read().decode('utf-8'))

    assert p.json_url, 'Failed to find Microsoft JSON'
    with urlopen(p.json_url) as f:
        data = json.load(f)

    return [
        IPvXRange(
            address=IPv6Network(a) if ':' in a else IPv4Network(a),
            region=e['properties']['region'],
            service=f'MICROSOFT::{e["properties"]["systemService"] or "GENERIC"}'.upper(),
        )
        for e in data['values']
        for a in e['properties']['addressPrefixes']
    ]


__all__ = [
    'IPvXRange',
    'fetch_amazon_ip_ranges',
    'fetch_google_ip_ranges',
    'fetch_microsoft_ip_ranges',
]
