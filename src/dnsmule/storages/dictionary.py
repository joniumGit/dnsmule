from typing import Optional

from ..api import Storage, Domain, Result


class DictStorage(Storage):
    type = 'dict'

    def __init__(self):
        super().__init__()
        self._dict = {}

    def store(self, result: Result):
        self._dict[result.name] = result

    def fetch(self, domain: Domain) -> Optional[Result]:
        if domain in self._dict:
            return self._dict[domain]


__all__ = [
    'DictStorage',
]
