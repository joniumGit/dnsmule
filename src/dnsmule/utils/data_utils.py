from pathlib import Path
from typing import Union


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
            data = map(lambda r: r[1].strip(), csv.reader(f))
        else:
            data = map(lambda s: s.strip(), f)
        if limit < 0:
            yield from iter(data)
        else:
            data = iter(data)
            for _, v in zip(range(limit), data):
                yield v


__all__ = [
    'load_data',
]
