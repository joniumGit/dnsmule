from csv import DictReader
from typing import Iterable, Mapping

from ..api import Backend, Record, Domain, RRType


class CSVBackend(Backend):
    """
    For loading data from CSV files

    It is possible to define the format and overrides for columns::

        file    <str>   Input file
        limit   <int>   Limits the iterations

        config['domain', 'record', 'data']
            Can be used to override CSV fields
            used for loading data into Records
    """
    type = 'csv'

    def __init__(
            self,
            *,
            file: str,
            limit: int = -1,
            domain: str = 'domain',
            record: str = 'record',
            data: str = 'rdata',
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

    def scan(self, domain: Domain, *types: RRType) -> Iterable[Record]:
        for line in self._generate_records():
            yield Record(
                Domain(line[self.domain].removesuffix('.')),
                RRType.from_any(line[self.record]),
                line[self.data],
            )
