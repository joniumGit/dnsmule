import json
from typing import Iterable, Optional

from .kvstorage import KeyValueStorage, JsonData, Query
from .. import Domain


class RedisStorage(KeyValueStorage):
    count: int = 100
    host: str
    port: int

    def __init__(self, **kwargs):
        super(RedisStorage, self).__init__(**kwargs)
        import redis
        self._client = redis.Redis(**kwargs, decode_responses=True)

    def __del__(self):
        if hasattr(self, '_client'):
            self._client.close()
            del self._client

    @property
    def client(self):
        return self._client

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
        return bool(self._client.exists(self.to_key(key)))

    def domains(self) -> Iterable[Domain]:
        yield from map(self.from_key, self._iterate(match=self.to_key(Domain('*'))))

    def size(self) -> int:
        return self._client.dbsize()


__all__ = [
    'RedisStorage',
    'Query',
]