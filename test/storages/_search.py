from abc import abstractmethod, ABC

import pytest

from dnsmule import Result, RRType, Domain
from dnsmule.storages.abstract import Storage, Query


class SearchTests(ABC):

    @abstractmethod
    def storage(self, *fixtures) -> Storage:
        """ABC
        """

    @pytest.mark.parametrize('domain,search_domains', [
        ('example.com', None),
        ('example.com', []),
        ('example.com', ['example.com']),
        ('*.example.com', ['*.example.com']),
        ('a.example.com', ['*.example.com']),
        ('*.a.example.com', ['*.example.com']),
        ('jira.a.example.com', ['jira.*']),
        ('example.com', ['*.com']),
        ('example.com', ['*com']),
    ])
    def test_match_domain(self, domain, search_domains, storage, ):
        result = Result(domain)
        storage.store(result)
        query = Query(domains=search_domains)
        assert [*storage.query(query)] == [result], 'Failed to match domain %r with %r' % (result.domain, query.domains)

    @pytest.mark.parametrize('types,search_types', [
        ([], None),
        ([], []),
        ([RRType.A], []),
        ([RRType.A], [RRType.A]),
        ([RRType.MX, RRType.TXT], [RRType.TXT]),
        ([65530], [65530]),
    ])
    def test_match_types(self, types, search_types, storage):
        result = Result(Domain(''))
        result.type.update(types)
        storage.store(result)
        query = Query(types=search_types)
        assert [*storage.query(query)] == [result], 'Failed to match types %r with %r' % (result.type, query.types)

    @pytest.mark.parametrize('tags,search_tags', [
        ([], None),
        ([], []),
        (['DNS::REGEX::TEST'], []),
        (['DNS::REGEX::TEST'], ['DNS::REGEX::TEST']),
        (['DNS::REGEX::TEST'], ['*::TEST']),
        (['DNS::REGEX::TEST'], ['DNS::*']),
        (['DNS::REGEX::TEST'], ['*::REGEX::*']),
        (['DNS::REGEX::TEST'], ['*DNS::*']),
        (['DNS::REGEX::TEST'], ['*::TEST*']),
    ])
    def test_match_tags(self, tags, search_tags, storage):
        result = Result(Domain(''))
        result.tags.update(tags)
        storage.store(result)
        query = Query(tags=search_tags)
        assert [*storage.query(query)] == [result], 'Failed to match tags %r with %r' % (result.tags, query.tags)

    @pytest.mark.parametrize('data,search_data', [
        ({}, None),
        ({}, []),
        ({'hello': 'world'}, ['hello']),
    ])
    def test_match_data(self, data, search_data, storage):
        result = Result(Domain(''))
        result.data.update(data)
        storage.store(result)
        query = Query(data=search_data)
        assert [*storage.query(query)] == [result], 'Failed to match data %r with %r' % (result.data, query.data)

    @pytest.mark.parametrize('domain,search_domains', [
        ('example.com', []),
        ('example.com', ['example.com']),
        ('a.example.com', ['*.example.com']),
        ('*.example.com', ['*.example.com']),
    ])
    @pytest.mark.parametrize('types,search_types', [
        ([], []),
        ([RRType.A], [RRType.A]),
    ])
    @pytest.mark.parametrize('tags,search_tags', [
        ([], []),
        (['DNS::REGEX::TEST'], ['DNS::REGEX::TEST']),
        (['DNS::REGEX::TEST'], ['*::REGEX::TEST']),
        (['DNS::REGEX::TEST'], ['DNS::REGEX::*']),
        (['DNS::REGEX::TEST'], ['*::REGEX::*']),
    ])
    @pytest.mark.parametrize('data,search_data', [
        ({}, []),
        ({'hello': 'world'}, ['hello']),
    ])
    def test_match_combined(
            self,
            domain,
            types,
            tags,
            data,
            search_domains,
            search_types,
            search_tags,
            search_data,
            storage,
    ):
        result = Result(domain)
        result.type.update(types)
        result.tags.update(tags)
        result.data.update(data)
        storage.store(result)
        query = Query(
            domains=search_domains,
            types=search_types,
            tags=search_tags,
            data=search_data,
        )
        assert [*storage.query(query)] == [result], 'Failed to match %r with %r' % (result, query)
