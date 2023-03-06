from typing import Set, Dict, Collection, Iterable, Any

DomainGroup = Dict[str, Collection[str]]


def lmerge(a: Dict[str, Any], b: Dict[str, Any]):
    """Left merge two dicts

    Left merging merges all values from the right dictionary into the left one.
    Any value not present in the left one is added as is.
    Any value with an incompatible type will raise TypeError.

    Merges most common builtin types to the left type.

    Example:  a: list + b: frozenset => list
    Example:  a: tuple + b: list => tuple
    Example:  a: frozenset + b: list => frozenset

    **Note:** Merging is recursive

    **Note:** Merging immutable collections does not preserve instance reference

    :raises TypeError: If value types are incompatible
    """
    for k in b:
        if k not in a:
            a[k] = b[k]
        elif not isinstance(b[k], type(a[k])) and not (
                isinstance(a[k], (list, set, tuple, frozenset))
                and isinstance(b[k], (list, set, tuple, frozenset))
        ):
            if isinstance(a[k], list):
                a[k].append(b[k])
            elif isinstance(a[k], set):
                a[k].add(b[k])
            elif isinstance(a[k], tuple):
                a[k] = (*a[k], b[k])
            elif isinstance(a[k], frozenset):
                a[k] = frozenset((*a[k], b[k]))
            else:
                raise TypeError(f'Value types for key {k} are incompatible a: {type(a[k])} b: {type(a[k])}')
        elif isinstance(a[k], dict):
            lmerge(a[k], b[k])
        elif isinstance(a[k], list):
            a[k].extend(b[k])
        elif isinstance(a[k], set):
            a[k].update(b[k])
        elif isinstance(a[k], tuple):
            a[k] = (*a[k], *b[k])
        elif isinstance(a[k], frozenset):
            a[k] = frozenset((*a[k], *b[k]))
        else:
            a[k] += b[k]


def process_domains(*domains: str) -> Set[str]:
    """De-duplicates and removes star domains from the input and creates all valid super domains
    
    *.a.b.c will have the * removed and ['a.b.c', 'b.c'] will be returned.

    >>> domain_data = ['*.b.c', 'a.b.c', 'b.c', 'a.b.c']
    >>> {*process_domains(*domain_data)} == {'b.c', 'a.b.c'} # Order is not guaranteed!
    True
    """
    return {*(d.lstrip('*.') for d in domains), *('.'.join(d.split('.')[-2:]) for d in domains)}


def group_domains_filtered_by(suffix: str, data: Iterable[str]) -> DomainGroup:
    """Groups all subdomains under the same parent domain filtered by the given suffix

    >>> domain_data = ['a.b.c', 'd.b.c', 'b.c', 'd.d']
    >>> grouped_domains = group_domains_filtered_by('.c', domain_data)
    >>> grouped_domains['b.c'] == {*domain_data[:-1]} # The last d.d is filtered out
    True
    """
    return group_domains(data, suffix=suffix)


def group_domains(data: Iterable[str], suffix: str = '') -> DomainGroup:
    """Groups domains and optionally filters by suffix

    >>> domain_data = ['a.b.c', 'd.b.c', 'b.c', 'd.d']
    >>> grouped_domains = group_domains(domain_data)
    >>> grouped_domains['b.c'] == {*domain_data[:-1]}
    True
    >>> grouped_domains['d.d'] == {domain_data[-1]}
    True
    """
    domains = {}
    for data in data:
        if not suffix or data.endswith(suffix):
            parts = data.split('.')
            parent_domain = '.'.join(parts[-2:])
            if parent_domain not in domains:
                domains[parent_domain] = {parent_domain}
            if len(parts) > 2:
                for i in range(-len(parts), -2):
                    domains[parent_domain].add('.'.join(parts[i:]))
    return domains


def generate_most_common_subdomains(grouped_domains: DomainGroup, count: int):
    """Generates first left subdomains more common than the given count

    >>> [*generate_most_common_subdomains({'a.b': ['a.a.b', 'c.a.b', 'a.a.b'], 'b.b.': {'a.b.b'}}, 1)]
    [('a', 2)]
    """
    subdomains = {}
    for _, domains in grouped_domains.items():

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

    yield from sorted(filter(lambda t: t[1] > count, subdomains.items()), key=lambda t: t[1], reverse=True)


if __name__ == '__main__':  # pragma: nocover
    import doctest

    __name__ = 'dnsmule.utils.misc'
    __package__ = 'dnsmule.utils'

    doctest.testmod()

__all__ = [
    'process_domains',
    'group_domains_filtered_by',
    'generate_most_common_subdomains',
    'lmerge',
    'DomainGroup',
    'group_domains',
]
