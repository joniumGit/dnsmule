from typing import Any

import pytest

from dnsmule import DNSMule, RRType, Backend, Rules, Record, Result, DictStorage, Domain


class SimpleBackend(Backend):
    def __init__(self, record_to_return: Any):
        self.record_to_return = record_to_return

    def scan(self, *_):
        yield self.record_to_return


@pytest.fixture
def domain():
    yield 'example.com'


@pytest.fixture
def tag():
    yield 'TEST'


@pytest.fixture
def ruleset(tag):
    rules = Rules()
    rules.register(RRType.TXT, lambda _, result: result.tags.add(tag))
    yield rules


@pytest.fixture
def record(ruleset, domain):
    yield Record(
        name=Domain(domain),
        type=[*ruleset.records][0],
        data='test',
    )


@pytest.fixture
def mule(ruleset, record):
    yield DNSMule(
        rules=ruleset,
        backend=SimpleBackend(record),
        storage=DictStorage(),
    )


def test_mule_scan_returns_result(mule, domain):
    with mule:
        result = mule.scan(domain)

    assert result is not None, 'Failed to get result'


def test_mule_scan_loads_and_updates_existing_result(mule, domain, record):
    existing_result = Result(
        name=Domain(domain),
        types={},
        tags={'existing'},
        data={},
    )

    def assertion(_, scan_result):
        assert scan_result is existing_result
        scan_result.tags.add('test')

    mule.rules = Rules()
    mule.rules.register(record.type, assertion)

    with mule:
        mule.storage.store(existing_result)
        result = mule.scan(domain)

    assert result is existing_result, 'Result changed'
    assert result.tags == {'existing', 'test'}, 'Failed to update result'


def test_mule_scan_normal_rule_runs(mule, domain, tag):
    with mule:
        mule.scan(domain)

    stored_result: Result = mule.storage.fetch(Domain(domain))
    assert stored_result.tags == {tag}, 'Failed to run rule'


def test_mule_scan_normal_rule_does_not_run_without_proper_type(record):
    domain = record.name
    record.type = RRType.A

    mule = DNSMule(
        rules=Rules(),
        backend=SimpleBackend(record),
        storage=DictStorage(),
    )

    mule.rules.register(RRType.TXT, lambda _, res: res.tags.add('a'))

    with mule:
        mule.scan(domain)

    stored_result: Result = mule.storage.fetch(Domain(domain))
    assert stored_result.tags != {}, 'Ran rule without matching record type'


def test_mule_scan_batch_rule_runs(mule, domain, tag):
    mule.rules.register_batch(rule=lambda _, sr: sr.tags.add('batch'))

    with mule:
        mule.scan(domain)

    stored_result: Result = mule.storage.fetch(Domain(domain))
    assert stored_result.tags == {tag, 'batch'}, 'Failed to run batch rule'


def test_mule_scan_any_record_rule_runs(mule, domain, tag):
    mule.rules.register_any(rule=lambda _, sr: sr.tags.add('any'))

    with mule:
        mule.scan(domain)

    stored_result: Result = mule.storage.fetch(Domain(domain))
    assert stored_result.tags == {tag, 'any'}, 'Failed to run RRType.ANY rule'
