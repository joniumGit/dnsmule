import csv
import sys


def load_data(file: str):
    with open(file, 'r') as f:
        for row in csv.reader(f):
            yield row[1]


if __name__ == '__main__':
    fi_domains = {}
    for data in load_data(sys.argv[1]):
        if data.endswith('.fi'):
            parts = data.split('.')
            parent_domain = '.'.join(parts[-2:])
            if parent_domain not in fi_domains:
                fi_domains[parent_domain] = {parent_domain}

            if len(parts) > 2:
                for i in range(-len(parts), -2):
                    fi_domains[parent_domain].add('.'.join(parts[i:]))

    subdomains = {}
    for vendor, domains in fi_domains.items():
        print(vendor, domains)

        subs = set()
        for domain in domains:
            parts = domain.split('.')
            if len(parts) > 2:
                subs.add(parts[-3])

        for sub in subs:
            if sub in subdomains:
                subdomains[sub] += 1
            else:
                subdomains[sub] = 1

    for subdomain, count in sorted(filter(lambda t: t[1] > 1, subdomains.items()), key=lambda t: t[1], reverse=True):
        print(subdomain, count)

    import asyncio
    from src.dnsmule.querier import query_records, RdataType

    records = {
        RdataType.TXT: [],
        RdataType.CNAME: [],
    }

    for vendor, domains in fi_domains.items():
        async def gather():
            tasks = [query_records(domain, RdataType.CNAME, RdataType.TXT) for domain in domains]
            for domain_results in await asyncio.gather(*tasks):
                for k, values in domain_results.items():
                    records[k].extend(v.to_text().removeprefix('"').removesuffix('"') for v in values)


        results = asyncio.run(gather())

    import json

    print(json.dumps(records, indent=4, default=str))

    import re

    o365 = re.compile(r'^(MS)=ms')
    ses = re.compile(r'^(amazonses):')
    azure = re.compile(r'^.*\.(azurewebsites)\.net')
    collection = re.compile(r'^(pardot|Zoo4).*=\w+$')
    generic_verification = re.compile(r'^(.+)(?:-(?:site|domain))?-verification=')
    generic_alt_0_verification = re.compile(r'^(.+)(?:site|domain)verification')
    generic_alt_1_verification = re.compile(r'^(.+)_verify_')
    generic_alt_2_verification = re.compile(r'^(\w+)(?:-code):')

    verifications = {}
    for r in records[RdataType.TXT]:
        for regex in [
            generic_verification,
            generic_alt_0_verification,
            generic_alt_1_verification,
            generic_alt_2_verification,
            o365,
            ses,
            azure,
            collection,
        ]:
            m = regex.search(r)
            if m:
                break
        if m:
            provider = m.group(1)
            if provider in verifications:
                verifications[provider] += 1
            else:
                verifications[provider] = 1

    print(json.dumps(verifications, indent=4, default=str))

    cnames = {
        'edgekey.net': 'Akamai CDN',
        'cloudflare.net': 'Cloudflare CDN',
        'cloudfront.net': 'Amazon Cloudfront',
        'github.io': 'GitHub Pages',
        'azureedge.net': 'Azure CDN',
        'awsglobalaccelerator.com': 'Amazon Accelerator',
        'amazonaws.com': 'Amazon Web Services',
        'simpli.fi': 'Simpli ADS',
        'doubleclick.net': 'Doubleclick',
    }
    providers = {k: 0 for k in cnames}
    for r in records[RdataType.CNAME]:
        for key in cnames:
            if key in r:
                providers[key] += 1
                break

    print(json.dumps(providers, indent=4, default=str))
