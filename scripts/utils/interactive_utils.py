from collections import defaultdict
from os import cpu_count
from typing import Callable, Coroutine, Iterable, Any, TypeVar, Dict, List

from dnsmule.backends.dnspython import query_records, DNSPythonBackend
from dnsmule.definitions import Result, Domain, RRType
from dnsmule.rules import Rules
from dnsmule.utils import DomainGroup
from dnsmule.utils.asyncio import BoundedWorkQueue, ProgressReportingBoundedWorkQueue

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
    from asyncio import get_event_loop

    if listener is None:
        queue = BoundedWorkQueue(work, bound)
    else:
        queue = ProgressReportingBoundedWorkQueue(work, bound, listener=listener)

    loop = get_event_loop()
    try:
        result = loop.run_until_complete(queue.complete())
    except KeyboardInterrupt:
        loop.run_until_complete(queue.cancel())
        loop.run_until_complete(loop.shutdown_asyncgens())
        result = [*queue.results]
    finally:
        loop.close()

    return result


def gather_interactive(
        grouped_domains: DomainGroup,
        progress_listener: Callable[[float], Coroutine]
) -> Dict[RRType, List[Result]]:
    """Gathers DNS records (TXT, CNAME) for all domains in a group

    Note: This can be cancelled early with a keyboard interrupt
    """
    records = {
        RRType.TXT: [],
        RRType.CNAME: [],
    }

    results = map_interactive(
        (
            query_records(domain, RRType.CNAME, RRType.TXT)
            for _, domains in grouped_domains.items()
            for domain in domains
        ),
        bound=cpu_count(),
        listener=progress_listener,
    )

    for domain_results in results:
        for k, values in domain_results.items():
            records[k].extend(v.to_text().removeprefix('"').removesuffix('"') for v in values)

    return records


def rules_interactive(
        domains: DomainGroup,
        rules: Rules,
        listener: Callable[[float], Coroutine[Any, Any, Any]] = None,
        all_domains: bool = False,
) -> Dict[RRType, List[Result]]:
    """Runs through a rule set with a bounded queue
    """

    backend = DNSPythonBackend(rules)

    def generate_domains():
        if all_domains:
            for domain, subs in domains.items():
                for sb in subs:
                    yield sb
        else:
            yield from domains.keys()

    async def run_rules(domain: str) -> Dict[RRType, Result]:
        results = defaultdict(list)
        async for result in backend.run_single(Domain(domain)):
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


__all__ = [
    'map_interactive',
    'gather_interactive',
    'rules_interactive',
]
