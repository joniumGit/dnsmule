from typing import List, Dict, Collection, Iterable

DOMAIN_GROUP_TYPE = Dict[str, Collection[str]]


def resolve_domain_from_certificates(ip: str, port: int = 443) -> List[str]:
    """Returns all names from a certificate retrieved from an ip-address

    Common name is the first one if available followed by any alternative names
    """
    from .certificates import collect_certificate  # Import here for not crashing on doctest
    cert = collect_certificate(ip, port=port)
    if cert is not None:
        return [cert.common, *cert.alts]
    else:
        return []


def subset_domains(*domains: str) -> List[str]:
    """De-duplicates and removes star domains from the input

    >>> domain_data = ['*.b.c', 'a.b.c', 'b.c', 'a.b.c']
    >>> {*subset_domains(*domain_data)} == {'b.c', 'a.b.c'} # Order is nor guaranteed!
    True
    """
    return [*{*(d.lstrip('*.') for d in domains), *('.'.join(d.split('.')[-2:]) for d in domains)}]


def group_domains(suffix: str, data: Iterable[str]) -> DOMAIN_GROUP_TYPE:
    """Groups all subdomains under the same parent domain filtered by the given suffix

    >>> domain_data = ['a.b.c', 'd.b.c', 'b.c', 'd.d']
    >>> grouped_domains = group_domains('.c', domain_data)
    >>> grouped_domains['b.c'] == {*domain_data[:-1]} # The last d.d is filtered out
    True
    """
    domains = {}
    for data in data:
        if data.endswith(suffix):
            parts = data.split('.')
            parent_domain = '.'.join(parts[-2:])
            if parent_domain not in domains:
                domains[parent_domain] = {parent_domain}

            if len(parts) > 2:
                for i in range(-len(parts), -2):
                    domains[parent_domain].add('.'.join(parts[i:]))
    return domains


if __name__ == '__main__':
    import doctest
    import pathlib

    __module__ = str(pathlib.Path(__file__).parent())  # Set this for relative import
    doctest.testmod()

__all__ = [
    'subset_domains',
    'resolve_domain_from_certificates',
    'group_domains',
    # Types
    'DOMAIN_GROUP_TYPE',
]
