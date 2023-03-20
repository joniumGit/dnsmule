from pathlib import Path
from typing import AsyncGenerator, Any

import pytest

from dnsmule import DNSMule, RRType
from dnsmule.backends.abstract import Backend
from dnsmule.definitions import Domain, Record, Result
from dnsmule.rules import Rules, Rule


class SimpleBackend(Backend):
    record_to_return: Any

    def _query(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        yield self.record_to_return


def dummy(_):
    pass


def test_with_existing_backend_and_rules():
    rules = Rules()
    mule = DNSMule.make(rules=rules, backend=SimpleBackend())
    assert type(mule.backend) == SimpleBackend, 'Failed to persist backend'
    assert mule.rules is rules, 'Failed to persist rules'


def test_empty_init_raises():
    with pytest.raises(ValueError):
        DNSMule(None, None, None, None)


def test_getitem_no_data():
    data = DNSMule.make().result('adaadwda')
    assert data is None, 'Returned something from key that does not exist'


def test_load_from_file():
    mule = DNSMule.load(Path(__file__).parent / 'sample.yml')
    assert mule.rules.size() != 0
    assert mule.plugins.contains('plugin.noop')
    assert mule.backend.__class__.__name__ == 'NOOPBackend'
    assert mule.storage.__class__.__name__ == 'DictStorage'


def test_getitem_with_data():
    mule = DNSMule.make()
    mule.scan('a')

    result = mule.result('a')
    assert len(result) == 0, 'Returned non-empty result'

    result = mule.result(Domain('a'))
    assert len(result) == 0, 'Returned non-empty result'


def test_append_rules():
    mule = DNSMule.make()
    assert len(mule.rules) == 0, 'Rules not empty'
    mule.append(Path(__file__).parent / 'loading' / 'sample_2.yml')
    assert len(mule.rules) != 0, 'Rules still empty'


def test_run_adds_domains():
    mule = DNSMule.make()
    assert len(mule.storage) == 0, 'Mule not empty on creation'
    mule.scan('a', 'b')
    assert len(mule.storage) == 2, 'Mule did not store domain'


def test_run_adds_domains_from_iterable():
    mule = DNSMule.make()
    assert len(mule.storage) == 0, 'Mule not empty on creation'
    mule.scan(iter(['a', 'b']))
    assert len(mule.storage) == 2, 'Mule did not store domain'


def test_run_adds_tags():
    def pass_transparent(o):
        return o

    rules = Rules()
    rules.process = pass_transparent

    record = Record(Domain('a'), RRType.A, 'a')
    record.tag('abcd')
    backend = SimpleBackend()
    backend.record_to_return = record

    mule = DNSMule.make(rules=rules, backend=backend)
    mule.scan('a')

    assert mule.result('a').tags == {'abcd'}, 'Failed to add result'


def test_make_persists_objects():
    rules = object()
    backend = object()
    storage = object()
    plugins = object()
    m = DNSMule.make(rules, backend, storage, plugins)
    assert m.rules is rules, 'Failed to persist rules'
    assert m.backend is backend, 'Failed to persist backend'
    assert m.storage is storage, 'Failed to persist storage'
    assert m.plugins is plugins, 'Failed to persist plugins'


def test_run_persisting_result():
    def return_result(r):
        new_result = Result(domain=r.domain)
        if 'hello' not in r.result.data:
            new_result.data['hello'] = ['world']
        return new_result

    rules = Rules()
    rules.append(RRType.TXT, Rule(f=return_result))

    backend = SimpleBackend()
    record = Record(Domain('a.com'), RRType.TXT, 'abcd')
    backend.record_to_return = record

    mule = DNSMule.make(rules=rules, backend=backend)

    result = Result(record.domain, initial_type=RRType.A)
    result.tag('a')
    mule.storage.store(result)
    assert mule.result(record.domain) is not None, 'Failed to store result'

    mule.scan(record.domain)
    mule.scan(record.domain)

    stored_result: Result = mule.result(record.domain)
    assert stored_result.type == {RRType.TXT, RRType.A}, 'Failed to add type'
    assert stored_result.data == {'hello': ['world']}, 'Failed to prevent duplicate data'
    assert stored_result.tags == {'a'}, 'Failed to persist tag'


def test_search_works(generate_result):
    mule = DNSMule.make()
    res = generate_result()
    res.tag('test')
    res.data['test_value'] = 'test_key'
    res.data['test_collection'] = ['test_1', 'test_2']
    res.types = {RRType.A, RRType.TXT}
    mule.storage.store(res)

    assert next(iter(mule.search(domains=[res.domain, 'b.com', 'c.com']))) is not None, 'Failed to find result'
    assert next(iter(mule.search(tags=['test']))) is not None, 'Failed to find result'
    assert next(iter(mule.search(data={'test_value': Any}))) is not None, 'Failed to find result'

    with pytest.raises(StopIteration):
        next(iter(mule.search(domains=[res.domain[1:]], tags=['test'])))


def test_search_works_2(generate_result):
    mule = DNSMule.make()

    res = generate_result()
    res.type.add(RRType.A)
    mule.storage.store(res)

    assert next(iter(mule.search(types=['A', 'TXT']))) is not None, 'Failed to find result'
