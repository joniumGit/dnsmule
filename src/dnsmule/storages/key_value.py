from typing import Optional

from ..api import Storage, Domain, Result, RRType
from ..utils import jsonize


class AbstractKVStorage(Storage):
    type = 'abstract_kv'

    def __init__(self, **config):
        super().__init__()
        self.config = config

    def store(self, result: Result):
        self._set(result.name, {
            'types': sorted(RRType.to_text(value) for value in result.types),
            'tags': sorted(result.tags),
            'data': result.data,
        })

    def fetch(self, domain: Domain) -> Optional[Result]:
        json_data = self._get(domain)
        if json_data:
            return Result(
                name=domain,
                types={RRType.from_any(value) for value in json_data['types']},
                tags={*json_data['tags']},
                data=jsonize(json_data['data']),
            )

    def _set(self, key: str, value: dict) -> None:
        """Implement
        """

    def _get(self, key: str) -> Optional[dict]:
        """Implement
        """
