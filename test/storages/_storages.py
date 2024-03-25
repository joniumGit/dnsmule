from abc import ABC, abstractmethod


# noinspection PyMethodMayBeStatic
class StoragesTestBase(ABC):

    def test_fetch_returns_none(self, generate_result, storage):
        assert storage.fetch(generate_result().name) is None, 'Failed to return None'

    def test_persists_result_works(self, storage, generate_result):
        r = generate_result()
        storage.store(r)
        assert storage.fetch(r.name) == r, 'Failed to return result'

    def test_persists_data(self, storage, generate_result):
        r = generate_result()
        r.data['a'] = 1
        storage.store(r)
        assert storage.fetch(r.name) == r, 'Failed to return result with data'


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
