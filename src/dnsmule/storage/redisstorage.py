import json
from typing import Iterator, Union

import redis as redis

from .abstract import Storage
from .serialization import ResultMapper
from ..definitions import Result, Domain


class RedisStorage(Storage):
    _client: redis.Redis
    host: str
    port: int

    def __init__(self, **kwargs):
        super(RedisStorage, self).__init__(**kwargs)
        self._client = redis.Redis(**kwargs, decode_responses=True)

    def __del__(self):
        if hasattr(self, '_client'):
            self._client.close()

    def __contains__(self, key: Union[str, Domain]):
        return self._client.exists(f'DNSMULE::RESULT::{str(key)}')

    def __setitem__(self, key: Union[str, Domain], value: Union[Result, None]):
        self._client.set(
            f'DNSMULE::RESULT::{str(key)}',
            json.dumps(ResultMapper.to_json(value), default=repr)
            if value is not None else
            '',
        )

    def __getitem__(self, key: Union[str, Domain]):
        value = self._client.get(f'DNSMULE::RESULT::{str(key)}')
        if value:
            return ResultMapper.from_json(json.loads(value))

    def __delitem__(self, key: Union[str, Domain]) -> None:
        self._client.delete(f'DNSMULE::RESULT::{str(key)}')

    def __len__(self) -> int:
        """Total amount of keys in keyspace

        This is only approximate.
        This does not indicate only result count, rather all keys in the current db.
        """
        return self._client.dbsize()

    def __iter__(self) -> Iterator[str]:
        for k in self._client.scan_iter(match='DNSMULE::RESULT::*'):
            yield str(k).removeprefix('DNSMULE::RESULT::')

    def get_client(self):
        return self._client


__all__ = [
    'RedisStorage',
]
