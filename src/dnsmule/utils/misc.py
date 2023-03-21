from pathlib import Path
from typing import Union, Dict, Any, Iterable, Callable

from .iterables import limit as limit_iterable


def csv_stripped(line):
    return line[1].strip()


def txt_stripped(line):
    return line.strip()


def load_data(file: Union[str, Path], limit: int = -1):
    """Loads target data from either a .csv of .txt file

    If the file is a .csv file it is assumed to be of the form:

    * index1,target1
    * index2,target2

    Otherwise, it is assumed to be a file of the form:

    * target1
    * target2

    If the given ``limit < 0`` then all data is returned.
    """
    file = Path(file)
    with open(file, 'r') as f:
        if file.suffix == '.csv':
            import csv
            data = map(csv_stripped, csv.reader(f))
        else:
            data = map(txt_stripped, f)
        if limit < 0:
            yield from data
        else:
            yield from limit_iterable(data, n=limit)


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


def extend_set(data: Dict[str, Any], key: str, values: Iterable[Any]):
    target = []
    if key in data:
        values = [*data[key], *values]
    for v in values:
        if v not in target:
            target.append(v)
    data[key] = target


def transform_set(data: Dict[str, Any], key: str, f: Callable[[Any], Any]):
    if key in data:
        data[key] = [f(o) for o in data[key]]
    else:
        data[key] = []


__all__ = [
    'load_data',
    'lmerge',
    'extend_set',
    'transform_set',
]
