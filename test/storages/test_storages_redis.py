from abc import ABC

import pytest

from _storages import ContainerStorageTestBase


# noinspection PyMethodMayBeStatic
class StoragesTestRedisBase(ContainerStorageTestBase, ABC):

    @pytest.fixture(scope='class')
    def storage_params(self, redis_container):
        yield {**redis_container}

    @pytest.fixture(scope='function', autouse=True)
    def flush(self, storage):
        if storage:
            storage._client.flushdb(asynchronous=False)
            yield
            storage._client.flushdb(asynchronous=False)
        else:
            yield

    def test_size_is_approximate(self, storage, generate_result):
        assert storage.size() == 0, 'Was not empty'
        storage.store(generate_result())
        storage._client.set('a', 1)
        storage._client.set('b', 2)
        assert storage.size() != 1, 'Other keys did not show up in len'


class TestStoragesRedis(StoragesTestRedisBase):

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages import RedisStorage
        yield RedisStorage(**storage_params)


class TestStoragesRedisJson(StoragesTestRedisBase):

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages import RedisJSONStorage
        yield RedisJSONStorage(**storage_params)
