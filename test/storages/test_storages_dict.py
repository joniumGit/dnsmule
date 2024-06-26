import pytest

from _storages import StoragesTestBase
from dnsmule.storages import DictStorage


class TestDictStorage(StoragesTestBase):

    @pytest.fixture
    def storage(self):
        with DictStorage() as instance:
            yield instance
