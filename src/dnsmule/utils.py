from pathlib import Path
from typing import Union, TypeVar, Any, Dict, Tuple, Iterable

K = TypeVar('K')
V = TypeVar('V')
R = TypeVar('R')


def join_values(a: Dict[K, V], b: Dict[K, R]) -> Iterable[Tuple[V, R]]:
    """Yields the values from two dicts for keys that are present in both
    """
    for k, v in a.items():
        if k in b:
            yield v, b[k]


def csv_stripped(line):
    return line[1].strip()


def txt_stripped(line):
    return line.strip()


def load_data(file: Union[str, Path], limit: int = -1):
    """
    Loads target data from either a .csv or .txt file

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
            yield from (value for _, value in zip(range(limit), data))


def left_merge(a: Dict[str, Any], b: Dict[str, Any]):
    """
    Left merge two dicts

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
            left_merge(a[k], b[k])
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


def extend_set(data: Dict[str, Any], key: str, *values: Any):
    """
    Appends values to a list based set in a dictionary

    **Note:** This is inefficient as it uses list traversal to check duplicates

    **Note:** This also de-duplicates the existing collection
    """
    target = []
    if key in data:
        values = [*data[key], *values]
    for v in values:
        if v not in target:
            target.append(v)
    data[key] = target


def extend_list(data: Dict[str, Any], key: str, *values: Any):
    """
    Appends values to a list in a dictionary
    """
    if key in data:
        data[key] = [*data[key], *values]
    else:
        data[key] = [*values]


def jsonize(value):
    """
    Jsonizes a couple of outliers in the standard collections

    :param value: Anything
    :return: Something hopefully JSON compatible
    """
    if isinstance(value, dict):
        return {
            k: jsonize(v)
            for k, v in value.items()
        }
    elif isinstance(value, (list, tuple, set, frozenset)):
        return [
            jsonize(item)
            for item in value
        ]
    else:
        return value


__all__ = [
    'load_data',
    'left_merge',
    'extend_set',
    'extend_list',
    'join_values',
    'jsonize',
]
