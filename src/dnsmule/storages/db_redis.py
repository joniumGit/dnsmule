from json import loads, dumps
from typing import Optional

from .key_value import AbstractKVStorage


class RedisStorage(AbstractKVStorage):
    type = 'redis'

    def __enter__(self):
        import redis
        self._client = redis.Redis(**self.config, decode_responses=True)
        self._client.ping()
        return self

    def __exit__(self, *_):
        self._client.close()
        del self._client

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
