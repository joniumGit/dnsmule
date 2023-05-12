from abc import ABC, abstractmethod

import pytest

from _search import SearchTests
from dnsmule import Result, RRType
from dnsmule.storages import Query


# noinspection PyMethodMayBeStatic
class StoragesTestBase(SearchTests, ABC):

    def test_contains(self, generate_result, storage):
        r = generate_result()
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain'

    def test_does_not_contain(self, generate_result, storage):
        r = generate_result()
        assert not storage.contains(r.domain), 'Failed to not contain'

    def test_fetch_returns_none(self, generate_result, storage):
        assert storage.fetch(generate_result().domain) is None, 'Failed to return None'

    def test_delete(self, generate_result, storage):
        r = generate_result()
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain'
        storage.delete(r.domain)
        assert not storage.contains(r.domain), 'Contained after delete'

    def test_size(self, storage, generate_result):
        assert storage.size() == 0, 'Was not empty'
        storage.store(generate_result())
        assert storage.size() == 1, 'Did not show up in len'

    def test_iter_returns_all_results(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert {*storage.domains()} == {r1.domain, r2.domain}, 'Failed to produce a set'

    def test_iter_produces_results(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert all(map(lambda o: isinstance(o, Result), storage.results())), 'Failed to produce results from storage'

    def test_iter_into_a_map(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert {**storage} == {r1.domain: r1, r2.domain: r2}, 'Failed to produce expected result'

    def test_persists_result_works(self, storage, generate_result):
        r = generate_result()
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain stored'
        assert storage.fetch(r.domain) == r, 'Failed to return result'

    def test_persists_data(self, storage, generate_result):
        r = generate_result()
        r.data['a'] = 1
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain stored domain'
        assert storage.fetch(r.domain) == r, 'Failed to return result with data'

    def test_iter_domains(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert {*storage.domains()} == {r1.domain, r2.domain}, 'Failed to get correct domains'

    def test_iter_results(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert {*storage.results()} == {r1, r2}, 'Failed to get correct results'

    def test_search_empty(self, storage, generate_result):
        r1 = generate_result()
        storage.store(r1)
        assert [*storage.query(Query(
            domains=[],
            types=[],
            tags='',
        ))] == [r1], 'Failed to match with empty query'

    def test_search_domain_simple(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert [*storage.query(Query(domains=[r1.domain]))] == [r1], 'Failed to match %r' % r1.domain

    @pytest.mark.parametrize('search', [
        ['*.c.sample.com', 'b.example.com'],
        ['b.example.com'],
        ['*.c.example.com'],
        ['*.c.example.com', 'b.example.com'],
    ])
    def test_search_domain_no_match(self, storage, generate_result, search):
        r1 = generate_result()
        r2 = generate_result()
        r1.domain = 'a.example.com'
        storage.store(r1)
        storage.store(r2)
        assert [*storage.query(Query(domains=search))] == [], 'Matched domain not in search with %r' % search

    def test_search_domain_wildcard_parent_no_match(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        r1.domain = 'example.com'
        storage.store(r1)
        storage.store(r2)
        assert [*storage.query(Query(domains=['*.example.com']))] == [], 'Matched parent with wildcard'

    def test_search_match_multiple(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        r1.domain = 'a.example.com'
        r2.domain = 'b.example.com'
        storage.store(r1)
        storage.store(r2)
        assert {*storage.query(Query(domains=['*.example.com']))} == {r1, r2}, 'Failed to match all results'

    def test_search_type(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        r1.type.clear()
        r1.type.add(RRType.A)
        r2.type.clear()
        r2.type.add(RRType.TXT)
        storage.store(r1)
        storage.store(r2)
        assert [*storage.query(Query(types=[RRType.A]))] == [r1], 'Failed to match by type'

    def test_search_tag(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        r1.tags.clear()
        r1.tags.add('DNS::REGEX::SAMPLE::TAG1')
        r2.tags.clear()
        r2.tags.add('IP::REGEX::SAMPLE::TAG1')
        storage.store(r1)
        storage.store(r2)
        assert [*storage.query(Query(tags=['ABC::*', 'DNS::*']))] == [r1], 'Failed to match by tag regex'

    def test_search_data(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        r1['search-tag'] = {'hello': 'world'}
        storage.store(r1)
        storage.store(r2)
        try:
            assert [*storage.query(Query(data=['search-tag']))] == [r1], 'Failed to match by data'
        except NotImplementedError:
            pytest.skip('Storage Does not implement search for data')


# noinspection PyMethodMayBeStatic
class ContainerStorageTestBase(StoragesTestBase, ABC):

    @abstractmethod
    def storage_params(self, *fixtures):
        """Returns params to init storage
        """

    @abstractmethod
    def flush(self, storage):
        """Flushes storage
        """

    def test_has_client(self, storage, storage_params):
        r = type(storage)(**storage_params)
        assert r._client is not None, 'Failed to match'

    def test_del_closes_client(self, storage, mock_closable, storage_params):
        if not hasattr(storage, '_client'):
            pytest.skip('No client for storage')
        s = type(storage)(**storage_params)
        s._client = mock_closable
        del s
        assert mock_closable.closed, 'Failed to close'

    def test_del_does_not_raise_without_client(self, storage, storage_params):
        if not hasattr(storage, '_client'):
            pytest.skip('No client for storage')
        r = type(storage)(**storage_params)
        del r._client
        del r
