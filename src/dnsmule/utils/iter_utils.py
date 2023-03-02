from typing import Iterable, TypeVar, Tuple, Callable, Literal

T = TypeVar('T')
R = TypeVar('R')


def limit(iterable: Iterable[T], *, n: int) -> Iterable[T]:
    for _, i in zip(range(n), iterable):
        yield i


def sort_by_item_value(item: Tuple[T, R]) -> R:
    return item[1]


def count_by(
        iterable: Iterable[T],
        f: Callable[[T], R],
        order: Literal['asc', 'desc'] = 'desc',
) -> Iterable[Tuple[R, int]]:
    reverse = order == 'desc'
    counts = {}
    for o in iterable:
        key = f(o)
        if key in counts:
            counts[key] += 1
        else:
            counts[key] = 1
    yield from sorted(counts.items(), key=sort_by_item_value, reverse=reverse)


__all__ = [
    'limit',
    'count_by',
]
