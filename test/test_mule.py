from typing import Any

from dnsmule import DNSMule, RRType, Backend, Rules, Record, Result, DictStorage, Domain


class SimpleBackend(Backend):
    record_to_return: Any

    def scan(self, *_):
        yield self.record_to_return


def test_run_persisting_records_result():
    def return_result(r, _):
        if 'hello' not in r.result.data:
            r.result.data['hello'] = ['world']

    rules = Rules()
    rules.register(RRType.TXT, rule=return_result)

    backend = SimpleBackend()
    record = Record(Domain('a.com'), RRType.TXT, 'abcd')
    backend.record_to_return = record

    mule = DNSMule(
        rules=rules,
        backend=backend,
        storage=DictStorage(),
    )

    with mule:
        result = Result(name=record.name, types=[RRType.A])
        result.tags.add('a')
        mule.storage.store(result)
        assert mule.storage.fetch(record.name) is not None, 'Failed to store result'

        result = mule.scan(record.name)
        assert result is not None, 'Failed to get result'
        assert result.data == {'hello': ['world']}, 'Failed to run rule'

    stored_result: Result = mule.storage.fetch(record.name)
    assert stored_result.types == {RRType.TXT, RRType.A}, 'Failed to add type'
    assert stored_result.data == {'hello': ['world']}, 'Failed to store data'
    assert stored_result.tags == {'a'}, 'Failed to persist tag'
