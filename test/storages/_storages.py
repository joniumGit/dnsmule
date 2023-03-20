from abc import ABC

from dnsmule import Result
from dnsmule.storages import Query


# noinspection PyMethodMayBeStatic
class StoragesTestBase(ABC):

    def test_contains(self, generate_result, storage):
        r = generate_result()
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain'

    def test_contains_2(self, generate_result, storage):
        r = generate_result()
        assert not storage.contains(r.domain), 'Failed to not contain'

    def test_get_default(self, generate_result, storage):
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

    def test_iter(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert {*storage.domains()} == {r1.domain, r2.domain}, 'Failed to produce expected result'

    def test_iter_2(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert all(map(lambda o: isinstance(o, Result), storage.results())), 'Failed to produce results'
        assert {*storage.results()} == {r1, r2}, 'Failed to produce expected result'

    def test_iter_3(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert {**storage} == {r1.domain: r1, r2.domain: r2}, 'Failed to produce expected result'

    def test_persists(self, storage, generate_result):
        r = generate_result()
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain'
        assert storage.fetch(r.domain) == r, 'Failed to return result'

    def test_persists_2(self, storage, generate_result):
        r = generate_result()
        r.data['a'] = 1
        storage.store(r)
        assert storage.contains(r.domain), 'Failed to contain'
        assert storage.fetch(r.domain) == r, 'Failed to return result'

    def test_search(self, storage, generate_result):
        r1 = generate_result()
        r2 = generate_result()
        storage.store(r1)
        storage.store(r2)
        assert [*storage.query(Query(
            domains=[r1.domain]
        ))] == [r1], 'Failed to produce expected result'
