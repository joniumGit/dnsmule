def load_data(file: str, limit: int = -1):
    """Loads target data from either a .csv of .txt file

    If the file is a .csv file it is assumed to be of the form:

    * index1,target1
    * index2,target2

    Otherwise, it is assumed to be a file of the form:

    * target1
    * target2

    If the given ``limit < 0`` then all data is returned.
    """
    with open(file, 'r') as f:
        if file.endswith('.csv'):
            import csv
            data = map(lambda r: r[1], csv.reader(f))
        else:
            data = map(lambda s: s.strip(), f)
        if limit < 0:
            yield from iter(data)
        else:
            data = iter(data)
            for _ in range(limit):
                yield next(data)


__all__ = [
    'load_data',
]
