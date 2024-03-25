from dnsmule import NoOpStorage, Domain, Result


def test_storages_noop_storage_returns_none():
    storage = NoOpStorage()
    storage.store(Result(name=Domain('a')))
    assert storage.fetch(Domain('a')) is None, 'Should return None'
