from typing import Iterable, Optional

import pytest

from dnsmule import Result, Domain
from dnsmule.storages import Storage, Query
from dnsmule.utils import KwargClass, empty


class SimpleStorage(Storage):

    def __init__(self):
        super(SimpleStorage, self).__init__()
        self.calls = []

    def size(self) -> int:
        self.calls.append('size')
        return 0

    def contains(self, domain: Domain) -> bool:
        self.calls.append('contains')
        return False

    def store(self, result: Result) -> None:
        self.calls.append('store')

    def fetch(self, domain: Domain) -> Optional[Result]:
        self.calls.append('fetch')
        return None

    def delete(self, domain: Domain) -> None:
        self.calls.append('delete')

    def results(self) -> Iterable[Result]:
        self.calls.append('results')
        yield from empty()

    def domains(self) -> Iterable[Domain]:
        self.calls.append('domains')
        yield from empty()

    def query(self, query: Query) -> Iterable[Result]:
        self.calls.append('search')
        yield from empty()


@pytest.fixture
def storage():
    yield SimpleStorage()


def test_using_context(storage):
    res = Result(Domain('a.com'))
    with storage.using(res) as result:
        assert result is res, 'Failed passthrough'
    assert storage.calls == ['fetch', 'store'], 'Called wrong methods'


def test_storage_adapter_getitem(storage):
    assert storage['a.com'] is None, 'Failed to default to None'
    assert storage.calls == ['fetch']


def test_storage_adapter_setitem(storage):
    storage[Domain('a.com')] = Result(Domain('a.com'))
    assert storage.calls == ['store']


def test_storage_adapter_iter(storage):
    _ = [*storage.__iter__()]
    assert storage.calls == ['domains']


def test_storage_adapter_len(storage):
    _ = len(storage)
    assert storage.calls == ['size']


def test_storage_adapter_del(storage):
    del storage['a.com']
    assert storage.calls == ['delete']


def test_storage_adapter_contains(storage):
    assert 'a' not in storage, 'Contained empty'
    assert storage.calls == ['contains'], 'Called actual contains impl too many times'


def test_storage_adapter_contains_2(storage):
    assert object() not in storage, 'Contained something that was not str'
    assert storage.calls == [], 'Called actual contains impl too many times'


def test_storage_adapter_setitem_mismatch_raises(storage):
    with pytest.raises(ValueError):
        storage[Domain('b.com')] = Result(Domain('a.com'))


def test_storage_is_abstract():
    with pytest.raises(TypeError):
        Storage()


def test_storage_is_kwarg_class():
    assert issubclass(Storage, KwargClass), 'Was not a keyword class'
