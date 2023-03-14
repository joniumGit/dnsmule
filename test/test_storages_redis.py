import os
import time

import pytest


def cached_skipper(f):
    from functools import wraps

    value = f()

    @wraps(f)
    def wrapper(*_, **__):
        return value

    return wrapper


@cached_skipper
def skip_redis():
    return max([
        os.system('docker --version'),
        os.system('python -c "import redis"'),
    ])


if not skip_redis():
    from dnsmule.storage.redisstorage import RedisStorage
    from dnsmule.definitions import Result, RRType


@pytest.fixture(scope='module')
def redis_storage():
    if not skip_redis():
        os.system('docker kill dnsmule-test-redis')
        assert os.system('docker run --rm -d -p 127.0.0.1:5431:6379 --name dnsmule-test-redis redis:alpine') == 0
        time.sleep(1)
        s = RedisStorage(host='127.0.0.1', port=5431)
        yield s
        assert os.system('docker kill dnsmule-test-redis') == 0
    else:
        raise ValueError('Invalid State')


@pytest.fixture(scope='function', autouse=True)
def flush(redis_storage):
    if redis_storage:
        redis_storage._client.flushdb(asynchronous=False)
        yield
        redis_storage._client.flushdb(asynchronous=False)
    else:
        yield


@pytest.mark.skipif(skip_redis(), reason='Docker or Redis not available')
class TestStoragesRedis:

    def test_storages_redis_contains(self, redis_storage):
        r = Result('example.com', RRType.A)
        redis_storage['a'] = r
        assert 'a' in redis_storage, 'Failed to contain'

    def test_storages_redis_get_default(self, redis_storage):
        assert redis_storage['a'] is None, 'Failed to contain'

    def test_storages_redis_del(self, redis_storage):
        r = Result('example.com', RRType.A)
        redis_storage['a'] = r
        assert 'a' in redis_storage, 'Failed to contain'
        del redis_storage['a']
        assert 'a' not in redis_storage, 'Failed to delete'

    def test_storages_redis_len(self, redis_storage):
        assert len(redis_storage) == 0, 'Was not empty'
        r = Result('example.com', RRType.A)
        redis_storage['a'] = r
        assert len(redis_storage) == 1, 'Did not show up in len'

    def test_storages_redis_len_approx(self, redis_storage):
        assert len(redis_storage) == 0, 'Was not empty'
        r = Result('example.com', RRType.A)
        redis_storage['a'] = r

        redis_storage._client.set('a', 1)
        redis_storage._client.set('b', 2)

        assert len(redis_storage) != 1, 'Other keys did not show up in len'

    def test_storages_redis_iter(self, redis_storage):
        r1 = Result('example.com', RRType.A)
        r2 = Result('a.example.com', RRType.A)
        redis_storage[r1.domain] = r1
        redis_storage[r2.domain] = r2
        assert {*redis_storage} == {r1.domain, r2.domain}, 'Failed to produce expected result'

    def test_storages_redis_del_closes_client(self):
        s = RedisStorage()
        called = []

        class MockClient:
            @staticmethod
            def close():
                called.append('close')

        s._client = MockClient()
        del s

        assert called == ['close'], 'Failed to close'

    def test_storages_redis_get_equals(self, redis_storage):
        r = Result('example.com', RRType.A)
        redis_storage['a'] = r
        assert 'a' in redis_storage, 'Failed to contain'
        assert redis_storage['a'] == r, 'Failed to return result'

    def test_storages_redis_save_none(self, redis_storage):
        redis_storage['a'] = None
        assert 'a' in redis_storage, 'Failed to contain'
        assert redis_storage['a'] is None, 'Failed to get None'

    def test_storages_redis_get_equals_2(self, redis_storage):
        r = Result('example.com', RRType.A)
        r.data['a'] = 1
        redis_storage['a'] = r
        assert 'a' in redis_storage, 'Failed to contain'
        assert redis_storage['a'] == r, 'Failed to return result'

    def test_storages_redis_get_client(self, redis_storage):
        assert redis_storage.get_client() is not None, 'Failed to return client'

    def test_storages_redis_del_does_not_raise_without_client(self):
        r = RedisStorage()
        del r._client
        del r
