from typing import Iterable, Optional, List

import pytest

from dnsmule import Domain
from dnsmule.storages.abstract import Query
from dnsmule.storages.kvstorage import JsonData, KeyValueStorage, result_from_json_data, result_to_json_data


class MockKVStorage(KeyValueStorage):
    calls: List[str]

    def __init__(self):
        super(MockKVStorage, self).__init__()
        self.calls = []
        self.values = []

    def _set(self, key: str, value: JsonData) -> None:
        self.calls.append('_set')
        self.values.append((key, value))

    def _get(self, key: str) -> Optional[JsonData]:
        self.calls.append('_get')
        if self.values:
            k, v = self.values.pop()
            assert key == k, 'Did not get expected key'
            return v

    def _del(self, key: str) -> None:
        self.calls.append('_del')

    def _iterate(self) -> Iterable[str]:
        self.calls.append('_iterate')
        yield from map(list.pop, self.values)

    def size(self) -> int:
        self.calls.append('size')
        return 0


@pytest.fixture
def mock_storage():
    yield MockKVStorage()


def test_store_calls_set(mock_storage, generate_result):
    mock_storage.store(generate_result())
    assert mock_storage.calls == ['_set']


def test_fetch_calls_get(mock_storage, generate_result):
    mock_storage.fetch(generate_result().domain)
    assert mock_storage.calls == ['_get']


def test_delete_calls_del(mock_storage, generate_result):
    mock_storage.delete(generate_result().domain)
    assert mock_storage.calls == ['_del']


def test_domains_calls_iterate(mock_storage, generate_result):
    _ = [*mock_storage.domains()]
    assert mock_storage.calls == ['_iterate']


def test_results_calls_iterate(mock_storage, generate_result):
    _ = [*mock_storage.results()]
    assert mock_storage.calls == ['_iterate']


def test_query_calls_iterate(mock_storage, generate_result):
    _ = [*mock_storage.query(query=Query())]
    assert mock_storage.calls == ['_iterate']


def test_size_calls_size(mock_storage, generate_result):
    mock_storage.size()
    assert mock_storage.calls == ['size']


@pytest.mark.parametrize('value', [
    'value',
    object(),
    [],
])
def test_pure_key_functions(mock_storage, value):
    key = mock_storage.to_key(Domain(value))
    assert mock_storage.is_key(key), 'to_key was not a key'
    assert mock_storage.from_key(key) == Domain(str(value)), 'Did not produce original result'


def test_json_function_inverse(generate_result):
    r = generate_result()
    assert result_from_json_data(result_to_json_data(r)) == r, 'Did not produce same result'


def test_store_expected_result(mock_storage, generate_result):
    r = generate_result()
    mock_storage.store(r)

    expected_key = (mock_storage.to_key(r.domain), result_to_json_data(r))
    assert mock_storage.values.pop() == expected_key, 'Did not set value as expected'


def test_fetch_expected_result(mock_storage, generate_result):
    r = generate_result()
    mock_storage.values.append((mock_storage.to_key(r.domain), result_to_json_data(r)))

    result = mock_storage.fetch(r.domain)
    assert result == r, 'Did not get expected result'


def test_contains_default_impl(mock_storage, generate_result):
    r = generate_result()
    assert not mock_storage.contains(r.domain), 'Contained domain'
    assert mock_storage.calls == ['_get'], 'Failed to call get for contains default impl'
