import json
import logging
from collections import defaultdict
from os import cpu_count
from typing import Callable, Coroutine, Iterable, Any, TypeVar, Dict, List

from dnsmule import DNSMule
from dnsmule.config import defaults, get_logger
from dnsmule.definitions import Result, Domain, RRType
from dnsmule.utils import DomainGroup
from dnsmule.utils import group_domains_filtered_by, generate_most_common_subdomains, load_data
from dnsmule.utils.async_utils import BoundedWorkQueue, ProgressReportingBoundedWorkQueue

T = TypeVar('T')


def map_interactive(
        work: Iterable[Coroutine[Any, Any, T]],
        bound: int,
        listener: Callable[[float], Coroutine[Any, Any, Any]] = None,
):
    """Use asyncio to map coroutines using a bounded queue

    note: This is not usable inside already async programs.

    note: This will catch a KeyboardInterrupt as the work cancellation call and will not propagate it
    """
    from asyncio import new_event_loop

    if listener is None:
        queue = BoundedWorkQueue(work, bound)
    else:
        queue = ProgressReportingBoundedWorkQueue(work, bound, listener=listener)

    loop = new_event_loop()
    try:
        result = loop.run_until_complete(queue.complete())
    except KeyboardInterrupt:
        loop.run_until_complete(queue.cancel())
        loop.run_until_complete(loop.shutdown_asyncgens())
        result = [*queue.results]
    finally:
        loop.close()

    return result


def rules_interactive(
        domains: DomainGroup,
        mule: DNSMule,
        listener: Callable[[float], Coroutine[Any, Any, Any]] = None,
        all_domains: bool = False,
) -> Dict[RRType, List[Result]]:
    """Runs through a rule set with a bounded queue
    """

    def generate_domains():
        if all_domains:
            for domain, subs in domains.items():
                for sb in subs:
                    yield sb
        else:
            yield from domains.keys()

    async def run_rules(domain: str) -> Dict[RRType, Result]:
        results = defaultdict(list)
        async for result in mule.get_backend().run_single(mule.rules, Domain(domain)):
            results[next(iter(result.type))].append(result)
        return {
            k: sum(v[1:], start=v[0]) if len(v) != 1 else v[0]
            for k, v in results.items()
        }

    work = iter(
        run_rules(domain)
        for domain in generate_domains()
    )

    data = map_interactive(work, bound=cpu_count(), listener=listener)
    reduced = {}

    for entry in data:
        for key, value in entry.items():
            if key not in reduced:
                reduced[key] = []
            reduced[key].append(value)

    return reduced


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


def default(o):
    if isinstance(o, set):
        return [RRType.to_text(i) if isinstance(i, int) else str(i) for i in o]
    else:
        return str(o)


async def print_progress(progress: float):
    """Prints progress to stdout
    """
    print(f'===> {progress:.2f}%', end='\r')


def main(file: str, rule_file: str, limit: int, count: int, skip_dump: bool, all_domains: bool):
    get_logger().setLevel(logging.INFO)
    get_logger().addHandler(logging.StreamHandler())
    mule = DNSMule.load(rule_file)

    print('Starting for', file, 'limiting to', limit, 'entries using DNS server ', defaults.DEFAULT_RESOLVER)
    data = load_data(file, limit=limit)
    fi_domains = group_domains_filtered_by('.fi', data)

    print('Showing common subdomains with count >', count)
    for subdomain, count in generate_most_common_subdomains(fi_domains, count):
        print(f'{count: >8d} {subdomain}')

    print('Fetching dns records, this will take a while...')
    results = rules_interactive(fi_domains, mule, listener=print_progress, all_domains=all_domains)
    print()

    print('Most common services from TXT records')
    verifications = sorted_tags(results, RRType.TXT)
    print(json.dumps(verifications, indent=4, default=str))

    print('Most common providers from CNAME records')
    providers = sorted_tags(results, RRType.CNAME)
    print(json.dumps(providers, indent=4, default=str))

    final_results = {}
    for _, rtype_results in results.items():
        for result in rtype_results:
            if result.domain not in final_results:
                final_results[result.domain] = result
            else:
                final_results[result.domain] += result

    from dataclasses import asdict
    final_results = [*map(asdict, filter(bool, final_results.values()))]

    if not skip_dump and input('Dump records to file? (y/n)') == 'y':
        with open(input('Give output filename:'), 'w') as f:
            json.dump(
                {'results': final_results},
                f,
                indent=4,
                default=default,
            )
    else:
        print(json.dumps(
            {'results': final_results},
            indent=4,
            default=default,
        ))


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
