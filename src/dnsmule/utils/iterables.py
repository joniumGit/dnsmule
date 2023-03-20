from collections import Counter, deque
from typing import Iterator, TypeVar, Tuple, Callable, Hashable, Any, Iterable

T = TypeVar('T')
R = TypeVar('R')
H = TypeVar('H', bound=Hashable)


def empty() -> Iterator[Any]:
    return iter([])


def select_second(from_tuple: Tuple[T, R]) -> R:
    return from_tuple[1]


def limit(iterable: Iterable[T], *, n: int) -> Iterable[T]:
    return map(select_second, zip(range(n), iterable))


def count_by(
        iterable: Iterable[T],
        f: Callable[[T], R],
        n: int = None,
) -> Iterable[Tuple[R, int]]:
    return iter(Counter(map(f, iterable)).most_common(n=n))


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


__all__ = [
    'limit',
    'count_by',
    'filter_locally_unique',
    'empty',
]
