from abc import ABC
from typing import Iterable

import pytest

from dnsmule import Domain, RRType, Record
from dnsmule.backends.abstract import Backend
from dnsmule.utils import KwargClass, empty


class DomainBackend(Backend):
    sentinel = object()

    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        yield DomainBackend.sentinel


class TypeBackend(Backend):
    sentinel = object()

    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        for _ in types:
            yield TypeBackend.sentinel


class ReceiverBackend(Backend):
    store = []

    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        self.store.extend(types)
        yield from empty()


@pytest.fixture(autouse=True)
def clear_receiver():
    yield
    ReceiverBackend.store.clear()


def test_single_yields_sentinel():
    backend = DomainBackend()
    result_iterator = iter(backend.single(Domain('a'), RRType.A, RRType.TXT))

    assert next(result_iterator) is DomainBackend.sentinel, 'Failed to produce sentinel value'

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_run_yields_sentinel():
    backend = DomainBackend()
    result_iterator = iter(backend.run((
        Domain(name)
        for name in ['a', 'b', 'c']
    ), RRType.A, RRType.TXT))

    assert next(result_iterator) is DomainBackend.sentinel, 'Failed to produce sentinel value'
    assert next(result_iterator) is DomainBackend.sentinel, 'Failed to produce sentinel value'
    assert next(result_iterator) is DomainBackend.sentinel, 'Failed to produce sentinel value'

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_query_receives_types_from_single():
    backend = ReceiverBackend()
    result_iterator = iter(backend.single(Domain('a'), RRType.A, RRType.TXT))

    with pytest.raises(StopIteration):
        next(result_iterator)

    assert ReceiverBackend.store == [RRType.A, RRType.TXT], 'Failed to pass types'


def test_query_receives_types_from_run():
    backend = ReceiverBackend()
    result_iterator = iter(backend.run([Domain('a'), Domain('b')], RRType.A, RRType.TXT))

    with pytest.raises(StopIteration):
        next(result_iterator)

    assert ReceiverBackend.store == [RRType.A, RRType.TXT] * 2, 'Failed to pass types'


def test_empty_types_yields_nothing():
    backend = TypeBackend()
    result_iterator = iter(backend.run(Domain(name) for name in ['a', 'b', 'c']))

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_types_yields_sentinel():
    backend = TypeBackend()
    result_iterator = iter(backend.single(Domain('a'), RRType.A, RRType.TXT))

    assert next(result_iterator) is TypeBackend.sentinel, 'Failed to produce sentinel value'
    assert next(result_iterator) is TypeBackend.sentinel, 'Failed to produce sentinel value'

    with pytest.raises(StopIteration):
        next(result_iterator)


def test_backend_is_kwarg_class():
    assert issubclass(Backend, KwargClass), 'Backend did not inherit KwargClass'


def test_backend_is_abstract():
    assert issubclass(Backend, ABC), 'Backend did not inherit from ABC'
