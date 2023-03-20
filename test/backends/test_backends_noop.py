import pytest

from dnsmule import Domain, RRType, Backend
from dnsmule.backends.noop import NOOPBackend


def test_query_yields_nothing():
    backend = NOOPBackend()
    result_iterator = iter(backend.single(Domain('a'), RRType.A))

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_inherits_backend():
    assert issubclass(NOOPBackend, Backend), 'Did not inherit from Backend'
