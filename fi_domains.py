from typing import TypeVar, Iterable, Callable, Tuple

T = TypeVar('T')
R = TypeVar('R')

with open('fi-domains.txt', 'r') as f:
    file_lines = f.read().splitlines(keepends=False)


def limit(iterable: Iterable[T], *, n: int) -> Iterable[T]:
    i = iter(iterable)
    for _ in range(n):
        yield next(i)


def sort_by_item_value(item: Tuple[T, int]) -> int:
    return item[1]


def count_by(iterable: Iterable[T], f: Callable[[T], R], order: str = 'desc') -> Iterable[Tuple[R, int]]:
    counts = {}
    for o in iterable:
        key = f(o)
        if key:
            if key in counts:
                counts[key] += 1
            else:
                counts[key] = 1
    yield from sorted(counts.items(), key=sort_by_item_value, reverse=order == 'desc')


def main(n: int = 10):
    print(f'Total entries: {len(file_lines)}')

    print()
    print('Top domains')
    for idx, (domain, count) in enumerate(limit(count_by(
            file_lines,
            lambda e: '.'.join(e.split('.')[-2:])
    ), n=n)):
        print(f'{idx: <5d} {count: >8d}', domain)

    print()
    print('Top sub-domains')
    for idx, (domain, count) in enumerate(limit(count_by(
            file_lines,
            lambda e: e.split('.')[-3] if len(e.split('.')) >= 3 else None
    ), n=n)):
        print(f'{idx: <5d} {count: >8d}', domain)


if __name__ == '__main__':
    main(100)
