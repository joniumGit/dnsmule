from collections import deque
from typing import TextIO, Collection, Hashable, Iterable, TypeVar

H = TypeVar('H', bound=Hashable)


def lagging_filter(lag: int):
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
    """Filters iterable to produce locally unique values

    This could be useful for removing duplicate values from a very long,
    but relatively sorted iterable.

    Requires the iterable values to be hashable.
    """
    return filter(lagging_filter(lag), iterable)


def domain_key(domain):
    return domain.split('.')[-2]


def collect_domains(file: TextIO):
    for line in file:
        parts = line.strip().split('.')
        yield '.'.join(parts[-2:])


def main(infile: TextIO, outfile: TextIO, generate_subdomains: Collection[str]):
    text = ''
    for domain in sorted(filter_locally_unique(collect_domains(infile), lag=1000)):
        text += f'{domain}\n'
        for sub in generate_subdomains:
            text += f'{sub}.{domain}\n'
    text = text.strip()
    outfile.write(text)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=argparse.FileType('r', encoding='utf8'))
    parser.add_argument('output', type=argparse.FileType('w', encoding='utf8'))
    parser.add_argument('subdomains', type=str, nargs='*')
    parser.add_argument('--top', type=int, default=20)
    args = parser.parse_args()

    if not args.input or not args.output:
        parser.print_help()
    else:
        with args.input as input_file, args.output as output_file:
            main(input_file, output_file, args.subdomains)
