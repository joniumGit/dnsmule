import json
from typing import Iterable, Optional

from .abstract import PrefixedKeyValueStorage, JsonData
from .. import Domain


class RedisStorage(PrefixedKeyValueStorage):
    count: int = 100
    host: str
    port: int

    def __init__(self, **kwargs):
        super(RedisStorage, self).__init__(**kwargs)
        import redis
        driver_args = self._kwargs
        driver_args['decode_responses'] = True
        self._client = redis.Redis(**driver_args)
        self._client.ping()

    def __del__(self):
        if hasattr(self, '_client'):
            self._client.close()
            del self._client

    def _set(self, key: str, value: JsonData) -> None:
        self._client.set(key, json.dumps(value))

    def _get(self, key: str) -> Optional[JsonData]:
        result = self._client.get(key)
        if result:
            return json.loads(result)

    def _del(self, key: str) -> None:
        self._client.delete(key)

    def _iterate(self, match='*') -> Iterable[str]:
        yield from self._client.scan_iter(match=match, count=self.count)

    def contains(self, key: Domain) -> bool:
        return bool(self._client.exists(self.domain_to_key(key)))

    def domains(self) -> Iterable[Domain]:
        yield from map(self.domain_from_key, self._iterate(match=self.domain_to_key(Domain('*'))))

    def size(self) -> int:
        return self._client.dbsize()


class RedisJSONStorage(RedisStorage):

    def _set(self, key: str, value: JsonData) -> None:
        self._client.json().set(key, '$', value)

    def _get(self, key: str) -> Optional[JsonData]:
        return self._client.json().get(key)


__all__ = [
    'RedisStorage',
    'RedisJSONStorage',
]
