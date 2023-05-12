import pytest

from test_storages_redis import ContainerStorageTestBase


class TestStoragesMongo(ContainerStorageTestBase):

    @pytest.fixture(scope='class')
    def storage_params(self, mongo_container):
        yield {**mongo_container}

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages.mongodbstorage import MongoStorage
        yield MongoStorage(**storage_params)

    @pytest.fixture(scope='function', autouse=True)
    def flush(self, storage):
        if storage:
            storage._client.drop_database(storage.database)
            yield
            storage._client.drop_database(storage.database)
        else:
            yield

    def test_client_property(self, storage, storage_params):
        r = type(storage)(**storage_params)
        assert r._collection is not None, 'Failed to have/create a collection'
