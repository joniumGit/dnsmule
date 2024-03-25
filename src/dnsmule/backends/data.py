from typing import Iterable

from ..api import Backend, Record, Domain, RRType


class DataBackend(Backend):
    """
    Gets data from config

    Data is structured as a map from a Domain to a set of records::

        www.example.com : [
            www.example.com IN  A    127.0.0.1,
            www.example.com IN  TXT  hello world,
        ]
    """
    type = 'data'

    def __init__(
            self,
            **config,
    ):
        super(DataBackend, self).__init__()
        self.config = config

    def scan(self, domain: Domain, *types: RRType) -> Iterable[Record]:
        types = {*types}
        for record in self.config.get(domain, []):
            if RRType.from_any(record['type']) in types:
                yield Record(
                    Domain(record['domain']),
                    RRType.from_any(record['type']),
                    record['data'],
                )
