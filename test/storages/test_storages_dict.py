import pytest

from _storages import StoragesTestBase
from dnsmule.storages.dictstorage import DictStorage


@pytest.fixture
def storage():
    yield DictStorage()


class TestDictStorage(StoragesTestBase):
    pass
