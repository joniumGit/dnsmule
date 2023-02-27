from dns.rdatatype import RdataType

from dnsmule.ip import ranges
from dnsmule.queries.queries import query
from dnsmule.utils import resolve_domain_from_certificates, subset_domains
from dnsmule.queries import a_to_ptr


async def main():
    import argparse

    async def load_services():
        import pickle
        try:
            with open('__service_cache__', 'rb') as f:
                services = pickle.load(f)
            print('Cache Loaded'.rjust(15, ' '))
        except FileNotFoundError:
            print('Cache Failed'.rjust(15, ' '))
            services = await ranges.fetch_ip_ranges()
            with open('__service_cache__', 'wb') as f:
                pickle.dump(services, f)
        return services

    async def fetch_and_display_records(host, record_type, **kwargs):

        dns_type = RdataType.from_text(record_type)
        response = await query(host, dns_type, **kwargs)
        print(f'{getattr(dns_type, "name", dns_type): >15}     ANSWER:', response.answer)
        print(f'{getattr(dns_type, "name", dns_type): >15}  AUTHORITY:', response.authority)
        print(f'{getattr(dns_type, "name", dns_type): >15} ADDITIONAL:', response.additional)

    def resolve_domain(host):

        domains = subset_domains(*resolve_domain_from_certificates(host))
        print(f'Domains From certificates for ip {host}', domains)

    async def a_type(host: str, services: dict):
        from ipaddress import IPv4Address, IPv6Address
        from typing import List

        from dns.asyncquery import udp_with_fallback
        from dns.message import make_query
        from dns.rdatatype import RdataType
        from dns.rdtypes.IN.A import A

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

    async def resolve_service(host):
        services = await load_services()
        await a_type(host, services)

    async def fetch_ptr_for_host(host):

        print('PTRs', await a_to_ptr(host))

    parser = argparse.ArgumentParser()
    parser.add_argument('--lookup', type=str)
    parser.add_argument('--ptr', type=str)
    parser.add_argument('--record', type=str, nargs='*')
    parser.add_argument('--target', type=str)
    parser.add_argument('--resolver', type=str)
    ns = parser.parse_args()

    if ns.lookup:
        resolve_domain(ns.lookup)
    elif ns.ptr:
        await fetch_ptr_for_host(ns.ptr)
    elif ns.target:
        if ns.record:
            for rt in ns.record:
                if ns.resolver:
                    await fetch_and_display_records(ns.target, rt, resolver=ns.resolver)
                else:
                    await fetch_and_display_records(ns.target, rt)
        else:
            await resolve_service(ns.target)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
