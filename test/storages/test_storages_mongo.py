import pytest

from test_storages_redis import ContainerStorageTestBase


class TestStoragesMongo(ContainerStorageTestBase):

    @pytest.fixture(scope='class')
    def storage_params(self, mongo_container):
        yield {**mongo_container}

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages import MongoStorage
        with MongoStorage(**storage_params) as instance:
            yield instance

    @pytest.fixture(scope='function', autouse=True)
    def flush(self, storage):
        if storage:
            storage._client.drop_database(storage.database)
            yield
            storage._client.drop_database(storage.database)
        else:
            yield
