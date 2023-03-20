from typing import Iterable

from .iterables import filter_locally_unique


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
