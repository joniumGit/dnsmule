from typing import Iterable, Optional

import pytest

from .api import Result, DNSMule, Backend, Record, Storage


def test_api_record_update_takes_keys_from_right():
    r1 = Result(
        name='a',
        tags=['a', 'b', 'c'],
        data={
            'a': 1,
            'b': 1,
        }
    )
    r2 = Result(
        name='a',
        tags=['c'],
        data={
            'c': 1
        }
    )
    r3 = Result(
        name='a',
        tags=['a', 'b', 'c'],
        data={
            'a': 1,
            'b': 1,
            'c': 1,
        }
    )

    r1.update(r2)
    result = r1

    assert result.name == r3.name, 'domain mismatch'
    assert result.tags == r3.tags, 'tags mismatch'
    assert result.data == r3.data, 'data mismatch'


def test_api_update_throws_on_domain_mismatch():
    r1 = Result(name='a')
    r2 = Result(name='b')
    with pytest.raises(ValueError):
        r1.update(r2)


class MockBackend(Backend):

    def __init__(self, *records):
        self._records = iter(records)

    def scan(self, domain: str, *records: int) -> Iterable[Record]:
        yield next(self._records, None)


class MockStorage(Storage):

    def __init__(self, *results):
        self._results = iter(results)

    def fetch(self, domain: str) -> Optional[Result]:
        return next(self._results, None)

    def store(self, result: Result) -> None:
        """No-op
        """


def test_api_use_result_from_domain_creates_result_on_none():
    mule = DNSMule(
        # Not required
        backend=None,
        storage=MockStorage(None),
    )

    with mule._use_result_for_domain('example.com') as result:
        assert result is not None, 'did not create a result instance'
