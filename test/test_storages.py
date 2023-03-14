from typing import Union, Iterator

import pytest

from dnsmule import Domain, Result
from dnsmule.storage.abstract import Storage
from dnsmule.storage.dictstorage import DictStorage


class SimpleStorage(Storage):

    def __setitem__(self, key: Union[str, Domain], value: Union[Result, None]) -> None:
        pass

    def __delitem__(self, key: Union[str, Domain]) -> None:
        pass

    def __getitem__(self, key: Union[str, Domain]) -> Union[Result, None]:
        pass

    def __len__(self) -> int:
        pass

    def __iter__(self) -> Iterator[str]:
        pass

    def __contains__(self, item: Union[str, Domain]):
        pass


def test_storages_dict_getting_does_not_raise():
    s = DictStorage()
    assert s['a'] is None, 'Did not reutn none'


def test_storages_dict_deleting_does_not_raise():
    s = DictStorage()
    del s['a']


def test_storages_dict_deleting():
    s = DictStorage()
    s['a'] = 1
    assert 'a' in s, 'Failed to set'
    del s['a']
    assert 'a' not in s, 'Failed to delete'


def test_storages_dict_len():
    s = DictStorage()
    s['a'] = 1
    s['b'] = 2
    assert len(s) == 2, ' Failed to produce len'


def test_storages_abstract_retains_kwargs():
    s = SimpleStorage(a=1, b='c')

    assert s.a == 1, ' Failed to persist'
    assert s.b == 'c', ' Failed to persist'


def test_storages_abstract_retains_kwargs_not_underscore():
    s = SimpleStorage(a=1, _b='c')

    assert s.a == 1, ' Failed to persist'
    with pytest.raises(AttributeError):
        s._b
