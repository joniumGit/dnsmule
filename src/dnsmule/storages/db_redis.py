from json import loads, dumps
from typing import Optional

from .utils import jsonize
from ..api import Storage, Domain, Result, RRType


class RedisStorage(Storage):
    type = 'redis'

    def __init__(self, **config):
        super().__init__()
        self.config = config

    def __enter__(self):
        import redis
        self._client = redis.Redis(**self.config, decode_responses=True)
        self._client.ping()
        return self

    def __exit__(self, *_):
        self._client.close()
        del self._client

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
        self._client.set(key, dumps(value))

    def _get(self, key: str) -> Optional[dict]:
        result = self._client.get(key)
        if result:
            return loads(result)


class RedisJSONStorage(RedisStorage):
    type = 'redis.json'

    def _set(self, key: str, value: dict) -> None:
        self._client.json().set(key, '$', value)

    def _get(self, key: str) -> Optional[dict]:
        return self._client.json().get(key)
