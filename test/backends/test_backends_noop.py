import pytest

from dnsmule import Domain, RRType, Backend
from dnsmule.backends.noop import NoOpBackend


def test_query_yields_nothing():
    backend = NoOpBackend()
    result_iterator = iter(backend.scan(Domain('a'), RRType.A))

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_inherits_backend():
    assert issubclass(NoOpBackend, Backend), 'Did not inherit from Backend'
