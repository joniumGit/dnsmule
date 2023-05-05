from threading import RLock
from typing import Iterable, Dict, Optional

from .abstract import Storage, Query, DefaultQuerier
from .. import Result, Domain


class DictStorage(Storage):
    _dict: Dict[Domain, Result]

    def __init__(self, **kwargs):
        super(DictStorage, self).__init__(**kwargs)
        self._dict = {}
        self._lock = RLock()

    def contains(self, domain: Domain) -> bool:
        return domain in self._dict

    def store(self, result: Result) -> None:
        with self._lock:
            self._dict = {**self._dict, result.domain: result}

    def fetch(self, domain: Domain) -> Optional[Result]:
        return self._dict.get(domain, None)

    def delete(self, domain: Domain) -> None:
        with self._lock:
            self._dict = {k: v for k, v in self._dict.items() if k != domain}

    def results(self) -> Iterable[Result]:
        return self._dict.values()

    def domains(self) -> Iterable[Domain]:
        for k in self._dict.keys():
            yield k

    def query(self, query: Query) -> Iterable[Result]:
        query = DefaultQuerier.create(query)
        for result in self.results():
            if query(result):
                yield result

    def size(self) -> int:
        return len(self._dict)


__all__ = [
    'DictStorage',
    'Query',
]
