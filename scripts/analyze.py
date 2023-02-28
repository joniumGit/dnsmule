import json
import logging

from dnsmule.config import defaults, get_logger
from dnsmule.definitions import RRType
from dnsmule.rules import load_config
from dnsmule.utils import group_domains, generate_most_common_subdomains, load_data
from utils.interactive_utils import rules_interactive


def sorted_tags(results, rtype):
    out = {}
    for result in results.get(rtype, []):
        for tag in result.tags:
            if tag not in out:
                out[tag] = 0
            out[tag] += 1
    return {
        k: v
        for k, v in sorted(out.items(), key=lambda t: t[1], reverse=True)
    }


async def print_progress(progress: float):
    """Prints progress to stdout
    """
    print(f'===> {progress:.2f}%', end='\r')


def main(file: str, rule_file: str, limit: int, count: int, skip_dump: bool, all_domains: bool):
    get_logger().setLevel(logging.INFO)
    get_logger().addHandler(logging.StreamHandler())
    rules = load_config(rule_file)

    print('Starting for', file, 'limiting to', limit, 'entries using DNS server ', defaults.DEFAULT_RESOLVER)
    data = load_data(file, limit=limit)
    fi_domains = group_domains('.fi', data)

    print('Showing common subdomains with count >', count)
    for subdomain, count in generate_most_common_subdomains(fi_domains, count):
        print(f'{count: >8d} {subdomain}')

    print('Fetching dns records, this will take a while...')
    results = rules_interactive(fi_domains, rules, listener=print_progress, all_domains=all_domains)
    print()

    print('Most common services from TXT records')
    verifications = sorted_tags(results, RRType.TXT)
    print(json.dumps(verifications, indent=4, default=str))

    print('Most common providers from CNAME records')
    providers = sorted_tags(results, RRType.CNAME)
    print(json.dumps(providers, indent=4, default=str))

    if not skip_dump and input('Dump records to file? (y/n)') == 'y':
        with open(input('Give output filename:'), 'w') as f:
            from dataclasses import asdict
            json.dump(
                {
                    k: [asdict(e) for e in v]
                    for k, v in results.items()
                },
                f,
                indent=4,
                default=str,
            )


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        import doctest

        doctest.testmod()
    else:

        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('input_file', metavar='FILE')
        parser.add_argument('rule_file', metavar='RULES')
        parser.add_argument('--sub-domain-count', '-sdc', dest='sdc', type=int, default=10)
        parser.add_argument('--limit', '-n', dest='limit', type=int, required=True)
        parser.add_argument('--skip-dump', dest='skip_dump', action='store_true', default=False)
        parser.add_argument('--all', dest='all', action='store_true', default=False)
        args = parser.parse_args()

        main(args.input_file, args.rule_file, args.limit, args.sdc, args.skip_dump, args.all)
