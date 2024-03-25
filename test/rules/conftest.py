import pytest

from dnsmule import Record, Domain, RRType, Result


@pytest.fixture
def record():
    yield Record(
        name=Domain('example.com'),
        type=RRType.A,
        data='127.0.0.1',
    )


@pytest.fixture
def result():
    yield Result(
        name=Domain('example.com'),
    )
