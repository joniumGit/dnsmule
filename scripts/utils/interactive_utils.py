from os import cpu_count
from typing import Callable, Coroutine, Iterable, Any, TypeVar, Dict, List

from dns.name import from_text as name_from_text
from dns.rdata import Rdata
from dns.rdatatype import RdataType

from dnsmule.queries import query_records, query
from dnsmule.rules import Result, process_message, Rules
from dnsmule.utils import DOMAIN_GROUP_TYPE
from dnsmule.utils.asyncio import BoundedWorkQueue, ProgressReportingBoundedWorkQueue

T = TypeVar('T')


def map_async_interactive(
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


def gather_records_interactive(
        grouped_domains: DOMAIN_GROUP_TYPE,
        progress_listener: Callable[[float], Coroutine]
) -> Dict[RdataType, List[Rdata]]:
    """Gathers DNS records (TXT, CNAME) for all domains in a group

    Note: This can be cancelled early with a keyboard interrupt
    """
    records = {
        RdataType.TXT: [],
        RdataType.CNAME: [],
    }

    results = map_async_interactive(
        (
            query_records(domain, RdataType.CNAME, RdataType.TXT)
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


def rules_async_interactive(
        domains: DOMAIN_GROUP_TYPE,
        rules: Rules,
        listener: Callable[[float], Coroutine[Any, Any, Any]] = None,
        all_domains: bool = False,
) -> Dict[RdataType, List[Result]]:
    """Runs through a rule set with a bounded queue
    """

    def generate_domains():
        if all_domains:
            for domain, subs in domains.items():
                for sb in subs:
                    yield sb
        else:
            yield from domains.keys()

    async def run_rules(domain: str) -> Dict[RdataType, Result]:
        response = await query(domain, *iter(t.unwrap() for t in rules.get_rtypes()))
        if response:
            return process_message(rules, name_from_text(domain), response)
        else:
            return {}

    work = iter(
        run_rules(domain)
        for domain in generate_domains()
    )

    data = map_async_interactive(work, bound=cpu_count(), listener=listener)
    reduced = {}

    for entry in data:
        for key, value in entry.items():
            if key not in reduced:
                reduced[key] = []
            reduced[key].append(value)

    return reduced


__all__ = [
    'map_async_interactive',
    'gather_records_interactive',
    'rules_async_interactive',
]
