from collections import deque
from typing import Iterable, TypeVar, Hashable

T = TypeVar('T')
R = TypeVar('R')
H = TypeVar('H', bound=Hashable)


def lagging_filter(lag: int):
    """
    Filters our values from an iterator that were recently seen

    The memory works using a first-in-first-out (FIFO) deque
    """
    values = set()
    latest = deque()

    if lag <= 0:
        raise ValueError('Invalid lag value')

    def filter_function(item):
        if item not in values:
            if len(values) >= lag:
                values.remove(latest.popleft())
            latest.append(item)
            values.add(item)
            return True
        else:
            return False

    return filter_function


def filter_locally_unique(iterable: Iterable[H], *, lag: int) -> Iterable[H]:
    """
    Filters iterable to produce locally unique values

    This could be useful for removing duplicate values from a very long,
    but relatively sorted iterable.

    Requires the iterable values to be hashable.
    """
    return filter(lagging_filter(lag), iterable)


def spread_domain(domain: str) -> Iterable[str]:
    """Spreads a domain into all valid super domains
    """
    parts = domain.strip().split('.')
    if parts[0] == '*' or parts[0] == '':
        parts = parts[1:]
    if len(parts) > 2:
        partial_domain = '.'.join(parts[-2:])
        yield partial_domain
        for i in range(-3, -len(parts) - 1, -1):
            partial_domain = f'{parts[i]}.{partial_domain}'
            yield partial_domain
    elif len(parts) == 2:
        yield '.'.join(parts)


def process_domains(domains: Iterable[str], *, lag: int = 100) -> Iterable[str]:
    """Best effort de-duplicates and removes star domains from the input and creates all valid super domains
    """
    return filter_locally_unique((value for domain in domains for value in spread_domain(domain)), lag=lag)


__all__ = [
    'process_domains',
]
