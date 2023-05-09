"""
This example uses a custom backend for DNSMule to read records from a file

The backend only needs to implement a single method that produces records.
The scan is then run with an arbitrary string to produce all records from the file.
A single rule is implemented to print out all CNAME records in the file.
"""
from pathlib import Path
from typing import Iterable

from dnsmule import DNSMule, Record, Domain, RRType
from dnsmule.backends.abstract import Backend


class FileBackend(Backend):
    """Implements a Backend for DNSMule that reads and splits lines in a file into a Record
    """
    file: str

    def _query(self, _: Domain, *types: RRType) -> Iterable[Record]:
        _types = {*types}
        with open(self.file, 'r') as f:
            for line in f:
                _type, _domain, _value = line.split(',')
                _type = RRType.from_any(_type)
                if _type in _types:
                    yield Record(domain=Domain(_domain), type=_type, data=_value)


mule = DNSMule.make(backend=FileBackend(file=Path(__file__).parent / 'example.domains'))


@mule.rules.add.CNAME
def aliases(record: Record):
    """Prints out all CNAME records found from the example file
    """
    print('FOUND A CNAME: ', record.domain, '>>', record.text)


if __name__ == '__main__':
    mule.scan('all domains in file')
