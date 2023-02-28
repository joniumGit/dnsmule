from typing import Iterable, TypeVar, Tuple, Callable

T = TypeVar('T')
R = TypeVar('R')


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


__all__ = [
    'limit',
    'count_by',
]
