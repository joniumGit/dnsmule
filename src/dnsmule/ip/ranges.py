from dataclasses import dataclass
from ipaddress import IPv4Network, IPv6Network
from typing import Set, Union, List

from httpx import AsyncClient

from ..config import get_logger


@dataclass
class IPvXRange:
    address: Union[IPv4Network, IPv6Network]
    region: str
    service: str


async def fetch_google_ip_ranges_goog() -> Set[IPv4Network]:
    host = 'https://www.gstatic.com/ipranges/goog.json'

    async with AsyncClient() as client:
        data = (await client.get(host)).json()

    get_logger().debug(
        '---GOOGLE GOOG DATA---\nModified:\n%s\nCount:\n%s',
        data['creationTime'],
        len(data['prefixes']),
    )

    return {
        IPv4Network(e['ipv4Prefix'])
        if 'ipv4Prefix' in e
        else IPv6Network(e['ipv6Prefix'])
        for e in data['prefixes']
    }


async def fetch_google_ip_ranges_cloud() -> List[IPvXRange]:
    host = 'https://www.gstatic.com/ipranges/cloud.json'

    async with AsyncClient() as client:
        data = (await client.get(host)).json()

    get_logger().debug(
        '---GOOGLE CLOUD DATA---\nModified:\n%s\nCount:\n%s',
        data['creationTime'],
        len(data['prefixes']),
    )

    return [
        IPvXRange(
            address=IPv4Network(e['ipv4Prefix']) if 'ipv4Prefix' in e else IPv6Network(e['ipv6Prefix']),
            region=e['scope'],
            service=f'GOOGLE::{e["service"]}'.upper(),
        )
        for e in data['prefixes']
    ]


async def fetch_google_ip_ranges():
    ranges_cloud = await fetch_google_ip_ranges_cloud()
    ranges_goog = await fetch_google_ip_ranges_goog()

    return [
        e
        for e in ranges_cloud
        if e.address not in ranges_goog
    ]


async def fetch_amazon_ip_ranges() -> List[IPvXRange]:
    host = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

    async with AsyncClient() as client:
        data = (await client.get(host)).json()

    get_logger().debug(
        '---AMAZON DATA---\nModified:\n%s\nCount:\n%s',
        data['createDate'],
        len(data['prefixes']),
    )

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
                address=IPv4Network(e['ipv6_prefix']),
                region=e['region'],
                service=f'AMAZON::{e["service"]}'.upper(),
            )
            for e in data['prefixes']
        )
    ]


async def fetch_microsoft_ip_ranges() -> List[IPvXRange]:
    host = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'

    from html.parser import HTMLParser
    async with AsyncClient() as client:
        json_url = ''

        class MicrosoftDownloadGrabber(HTMLParser):

            def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
                if tag == 'a':
                    attrs = {k: v for k, v in attrs}
                    if attrs.get('href', '').startswith('https://download.microsoft.com'):
                        nonlocal json_url
                        json_url = attrs['href']

        p = MicrosoftDownloadGrabber()
        p.feed((await client.get(host)).text)

        assert json_url != ''
        data = (await client.get(json_url)).json()

    get_logger().debug(
        '---MICROSOFT DATA---\nChange N:\n%s\nCount:\n%s',
        data['changeNumber'],
        len(data['values']),
    )

    return [
        IPvXRange(
            address=IPv6Network(a) if ':' in a else IPv4Network(a),
            region=e['properties']['region'],
            service=f'MICROSOFT::{e["properties"]["systemService"]}'.upper(),
        )
        for e in data['values']
        for a in e['properties']['addressPrefixes']
    ]


async def fetch_ip_ranges() -> List[IPvXRange]:
    services = [
        *(
            await fetch_google_ip_ranges()
        ),
        *(
            await fetch_amazon_ip_ranges()
        ),
        *(
            await fetch_microsoft_ip_ranges()
        ),
    ]

    per_service_counts = {}
    for e in services:
        s = e['service']
        if s in per_service_counts:
            per_service_counts[s] += 1
        else:
            per_service_counts[s] = 0

    from pprint import pprint
    pprint(per_service_counts, indent=4)

    return services
