import sys
from ipaddress import IPv4Network, IPv6Network, IPv4Address, IPv6Address
from typing import List

from dns.asyncquery import udp_with_fallback
from dns.message import make_query
from dns.rdatatype import RdataType, is_metatype
from dns.rdtypes.IN.A import A
from httpx import AsyncClient


async def fetch_google_ip_ranges_goog():
    host = 'https://www.gstatic.com/ipranges/goog.json'

    async with AsyncClient() as client:
        data = (await client.get(host)).json()

    print('---GOOGLE GOOG DATA---')
    print('Modified: ', data['creationTime'])
    print('Count: ', len(data['prefixes']))

    return {
        IPv4Network(e['ipv4Prefix'])
        if 'ipv4Prefix' in e
        else IPv6Network(e['ipv6Prefix'])
        for e in data['prefixes']
    }


async def fetch_google_ip_ranges_cloud():
    host = 'https://www.gstatic.com/ipranges/cloud.json'

    async with AsyncClient() as client:
        data = (await client.get(host)).json()

    print('---GOOGLE CLOUD DATA---')
    print('Modified:', data['creationTime'])
    print('Count:', len(data['prefixes']))

    return [
        {
            'address': IPv4Network(e['ipv4Prefix']) if 'ipv4Prefix' in e else IPv6Network(e['ipv6Prefix']),
            'region': e['scope'],
            'service': f'GOOGLE::{e["service"]}'.upper(),
        } for e in data['prefixes']
    ]


async def fetch_google_ip_ranges():
    ranges_cloud = await fetch_google_ip_ranges_cloud()
    ranges_goog = await fetch_google_ip_ranges_goog()

    return [
        e
        for e in ranges_cloud
        if e['address'] not in ranges_goog
    ]


async def fetch_amazon_ip_ranges():
    host = 'https://ip-ranges.amazonaws.com/ip-ranges.json'

    async with AsyncClient() as client:
        data = (await client.get(host)).json()

    print('---AMAZON DATA---')
    print('Modified:', data['createDate'])
    print('Count:', len(data['prefixes']))

    return [
        *(
            {
                'address': IPv4Network(e['ip_prefix']),
                'region': e['region'],
                'service': f'AMAZON::{e["service"]}'.upper(),
            }
            for e in data['prefixes']
        ),
        *(
            {
                'address': IPv6Network(e['ipv6_prefix']),
                'region': e['region'],
                'service': f'AMAZON::{e["service"]}'.upper(),
            }
            for e in data['ipv6_prefixes']
        )
    ]


async def fetch_microsoft_ip_ranges():
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

    print('---MICROSOFT DATA---')
    print('Change N:', data['changeNumber'])
    print('Count:', len(data['values']))

    return [
        {
            'address': IPv6Network(a) if ':' in a else IPv4Network(a),
            'region': e['properties']['region'],
            'service': f'MICROSOFT::{e["properties"]["systemService"]}'.upper(),
        }
        for e in data['values']
        for a in e['properties']['addressPrefixes']
    ]


async def fetch_ip_ranges():
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


async def main():
    import pickle

    try:
        with open('__service_cache__', 'rb') as f:
            services = pickle.load(f)
        print('Cache Loaded'.rjust(15, ' '))
    except FileNotFoundError:
        print('Cache Failed'.rjust(15, ' '))
        services = await fetch_ip_ranges()
        with open('__service_cache__', 'wb') as f:
            pickle.dump(services, f)

    host = sys.argv[1]

    for dns_type in RdataType:
        if not is_metatype(dns_type):
            q = make_query(host, dns_type)
            r, _ = await udp_with_fallback(q, '8.8.8.8')
            if len(r.answer) != 0:
                print(f'{dns_type.name: >15}', r.answer)

            import time
            time.sleep(0.1)

    q = make_query(host, RdataType.A)
    r, _ = await udp_with_fallback(q, '8.8.8.8')

    for a in r.answer:
        values: List[A] = [*a.items.keys()]
        for record in values:
            ip = record.address
            ip = IPv6Address(ip) if ':' in ip else IPv4Address(ip)
            for s in services:
                if ip in s['address']:
                    print('Found Match'.rjust(15, ' '), ip, s)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
