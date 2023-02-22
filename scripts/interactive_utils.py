from os import cpu_count
from typing import Callable, Coroutine, Iterable, Any, TypeVar

from dns.rdatatype import RdataType

from dnsmule.utils.asyncio import BoundedWorkQueue, ProgressReportingBoundedWorkQueue
from src.dnsmule.queries import query_records
from src.dnsmule.utils import DOMAIN_GROUP_TYPE

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


def gather_records_interactive(
        grouped_domains: DOMAIN_GROUP_TYPE,
        progress_listener: Callable[[float], Coroutine]
):
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


__all__ = [
    'map_async_interactive',
    'gather_records_interactive',
]
