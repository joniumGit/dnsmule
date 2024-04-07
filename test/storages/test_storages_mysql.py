from abc import ABC

import pytest

from _storages import ContainerStorageTestBase


# noinspection PyMethodMayBeStatic
class TestStoragesMySQL(ContainerStorageTestBase, ABC):

    @pytest.fixture(scope='class')
    def storage(self, storage_params):
        from dnsmule.storages import MySQLStorage
        with MySQLStorage(**storage_params) as instance:
            yield instance

    @pytest.fixture(scope='class')
    def storage_params(self, mysql_container):
        yield {**mysql_container}

    @pytest.fixture(scope='function', autouse=True)
    def flush(self, storage):
        if storage:
            c = storage._client.cursor()
            c.execute('DELETE FROM results')
            c.close()
            yield
            c = storage._client.cursor()
            c.execute('DELETE FROM results')
            c.close()
        else:
            yield
