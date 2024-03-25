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


class TestStoragesRedis(StoragesTestRedisBase):

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages import RedisStorage
        with RedisStorage(**storage_params) as instance:
            yield instance


class TestStoragesRedisJson(StoragesTestRedisBase):

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages import RedisJSONStorage
        with RedisJSONStorage(**storage_params) as instance:
            yield instance
