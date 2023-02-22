import json
import re

from dns.rdatatype import RdataType

from scripts.data_utils import load_data
from scripts.interactive_utils import gather_records_interactive
from src.dnsmule.config import defaults
from src.dnsmule.utils import group_domains, generate_most_common_subdomains


async def print_progress(progress: float):
    """Prints progress to stdout
    """
    print(f'===> {progress:.2f}%', end='\r')


def detect_regex(records):
    o365 = re.compile(r'^(MS)=ms')
    ses = re.compile(r'^(amazonses):')
    azure = re.compile(r'^.*\.(azurewebsites)\.net')
    collection = re.compile(r'^(pardot|Zoo4).*=\w+$')
    generic_verification = re.compile(r'^(.+)(?:-(?:site|domain))?-verification=')
    generic_alt_0_verification = re.compile(r'^(.+)(?:site|domain)verification')
    generic_alt_1_verification = re.compile(r'^(.+)_verify_')
    generic_alt_2_verification = re.compile(r'^(\w+)-code:')

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

    return verifications


def detect_cname(records):
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
    return {k: v for k, v in providers.items() if v > 0}


def main(file: str, limit: int, count: int, skip_dump: bool):
    print('Starting for', file, 'limiting to', limit, 'entries using DNS server ', defaults.DEFAULT_RESOLVER)
    data = load_data(file, limit=limit)
    fi_domains = group_domains('.fi', data)

    print('Showing common subdomains with count >', count)
    for subdomain, count in generate_most_common_subdomains(fi_domains, count):
        print(f'{count: >8d} {subdomain}')

    print('Fetching dns records, this will take a while...')
    records = gather_records_interactive(fi_domains, print_progress)
    print()

    print('Most common services from TXT records')
    verifications = detect_regex(records)
    print(json.dumps(verifications, indent=4, default=str))

    print('Most common providers from CNAME records')
    providers = detect_cname(records)
    print(json.dumps(providers, indent=4, default=str))

    if not skip_dump and input('Dump records to file? (y/n)') == 'y':
        with open(input('Give output filename:'), 'w') as f:
            json.dump(records, f, indent=4, default=str)


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        import doctest

        doctest.testmod()
    else:

        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', metavar='FILE')
        parser.add_argument('--sub-domain-count', '-sdc', dest='sdc', type=int, default=10)
        parser.add_argument('--limit', '-n', dest='limit', type=int, required=True)
        parser.add_argument('--skip-dump', dest='skip_dump', action='store_true', default=False)
        args = parser.parse_args()

        main(args.input_file, args.limit, args.sdc, args.skip_dump)
