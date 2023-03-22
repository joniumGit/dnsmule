import os
import time
from abc import ABC

import pytest

from _storages import StoragesTestBase


@pytest.cached
def skip_redis():
    return max([
        os.system('docker info'),
        os.system('python -c "import redis"'),
    ])


class StoragesTestRedisBase(StoragesTestBase, ABC):

    @pytest.fixture(scope='class')
    def container(self):
        if not skip_redis():
            os.system('docker kill dnsmule-test-redis')
            assert os.system(
                'docker run --rm -d -p 127.0.0.1:5431:6379 '
                '--name dnsmule-test-redis '
                'redis/redis-stack:latest'
            ) == 0
            time.sleep(1)
            yield {'host': '127.0.0.1', 'port': 5431}
            assert os.system('docker kill dnsmule-test-redis') == 0
        else:
            raise ValueError('Invalid State')

    @pytest.fixture(scope='function', autouse=True)
    def flush(self, storage):
        if storage:
            storage._client.flushdb(asynchronous=False)
            yield
            storage._client.flushdb(asynchronous=False)
        else:
            yield

    def test_del_closes_client(self, storage, mock_closable):
        s = type(storage)()
        s._client = mock_closable
        del s
        assert mock_closable.closed, 'Failed to close'

    def test_del_does_not_raise_without_client(self, storage):
        r = type(storage)()
        del r._client
        del r

    def test_client_property(self, storage):
        r = type(storage)()
        assert r.client is r._client, 'Failed to match'

    def test_size_is_approximate(self, storage, generate_result):
        assert storage.size() == 0, 'Was not empty'
        storage.store(generate_result())
        storage._client.set('a', 1)
        storage._client.set('b', 2)
        assert storage.size() != 1, 'Other keys did not show up in len'


@pytest.mark.skipif(skip_redis(), reason='Docker or Redis not available')
class TestStoragesRedis(StoragesTestRedisBase):

    @pytest.fixture(scope='class')
    def storage(self, container):
        from dnsmule.storages.redisstorage import RedisStorage
        yield RedisStorage(**container)


@pytest.mark.skipif(skip_redis(), reason='Docker or Redis not available')
class TestStoragesRedisJson(StoragesTestRedisBase):

    @pytest.fixture(scope='class')
    def storage(self, container):
        from dnsmule.storages.redisstorage import RedisStorage
        yield RedisStorage(**container, use_json=True)
