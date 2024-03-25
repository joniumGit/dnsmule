from csv import DictReader
from pathlib import Path
from typing import Iterable, Mapping, Union

from ..api import Backend, Record, Domain, RRType


class CSVBackend(Backend):
    """
    For loading data from CSV files.

    This is mainly used for loading loads of cached records that are to be reprocessed.
    This is not useful for actually querying csv files as by design this backend
    ignores the given scan parameters and simply reads data from the given CSV file.


    It is possible to define the format and overrides for columns::

        file    <str>   Input file
        limit   <int>   Limits the lines read from the CSV

        domain  <str>   Domain key (default: domain)
        record  <str>   Record key (default: record)
        data    <str>   Data key   (default: data)

        Can be used to override CSV fields
        used for loading data into Records

    **NOTE**: This backend ignores scan parameters!
    """
    type = 'csv'

    def __init__(
            self,
            *,
            file: Union[str, Path],
            limit: int = -1,
            domain: str = 'domain',
            record: str = 'record',
            data: str = 'data',
    ):
        super(Backend, self).__init__()
        self.file = file
        self.limit = limit
        self.domain = domain
        self.record = record
        self.data = data

    def __enter__(self):
        self._file = open(self.file, 'r')
        self._reader = DictReader(self._file)
        return self

    def __exit__(self, *_):
        del self._reader
        self._file.close()
        del self._file

    def _generate_records(self) -> Iterable[Mapping[str, str]]:
        limit = int(self.limit)
        if limit > 0:
            for _, line in zip(range(limit), self._reader):
                yield line
        else:
            yield from self._reader

    def scan(self, *_) -> Iterable[Record]:
        for line in self._generate_records():
            yield Record(
                Domain(line[self.domain].removesuffix('.')),
                RRType.from_any(line[self.record]),
                line[self.data],
            )
