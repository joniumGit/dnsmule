from dnsmule import DNSMule
from dnsmule.adapter import Adapter, patch_storage
from dnsmule.storages import Query


def add_loaded(result):
    result.data['loaded'] = True
    return result


def add_stored(result):
    result.data['stored'] = True
    return result


def test_patching_fetch(generate_result):
    result = generate_result()
    mule = DNSMule.make()
    mule.storage.store(result)

    patch_storage(mule.storage, Adapter(add_loaded, add_stored))
    result = mule.storage.fetch(domain=result.domain)

    assert result.data['loaded'], 'Failed to go through the adapter'


def test_patching_fetch_no_result(generate_result):
    mule = DNSMule.make()

    patch_storage(mule.storage, Adapter(add_loaded, add_stored))
    result = mule.storage.fetch(domain='example')

    assert result is None, 'Produced something other than what was intended'


def test_patching_results(generate_result):
    result = generate_result()
    mule = DNSMule.make()
    mule.storage.store(result)

    patch_storage(mule.storage, Adapter(add_loaded, add_stored))
    result = next(mule.storage.results())

    assert result.data['loaded'], 'Failed to go through the adapter'


def test_patching_query(generate_result):
    result = generate_result()
    mule = DNSMule.make()
    mule.storage.store(result)

    patch_storage(mule.storage, Adapter(add_loaded, add_stored))
    result = next(mule.storage.query(query=Query(domains=[result.domain])))

    assert result.data['loaded'], 'Failed to go through the adapter'


def test_patching_store(generate_result):
    result = generate_result()
    mule = DNSMule.make()
    old_method = mule.storage.fetch

    patch_storage(mule.storage, Adapter(add_loaded, add_stored))
    mule.storage.store(result)

    result = old_method(result.domain)
    assert result.data['stored'], 'Failed to go through the adapter on store'


def test_adapter_calls_correctly(generate_result):
    save = object()
    load = object()

    adapter = Adapter(lambda _: load, lambda _: save)

    assert adapter.from_storage(generate_result()) is load, 'Called the wrong method on load'
    assert adapter.to_storage(generate_result()) is save, 'Called the wrong method on save'
