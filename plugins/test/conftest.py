import pytest

from dnsmule import Record, RRType, Result, Domain


@pytest.fixture
def record():
    yield Record(Domain('example.com'), RRType.A, '127.0.0.1')


@pytest.fixture
def result(record):
    yield Result(record.name)
