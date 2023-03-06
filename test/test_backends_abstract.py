from typing import AsyncGenerator, Any

import pytest

from _async import async_test
from dnsmule import RRType
from dnsmule.backends import abstract
from dnsmule.definitions import Domain, Record
from dnsmule.rules import Rules


class BasicBackend(abstract.Backend):

    async def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        for t in types:
            yield t


def test_backend_abstract_is_abstract():
    with pytest.raises(TypeError):
        abstract.Backend()


def test_backend_abstract_kwargs():
    b = BasicBackend(a=1, b=[])
    assert b.a == 1 and b.b == [], 'Failed to set kwargs'


def test_backend_abstract_kwargs_no_underscore():
    b = BasicBackend(_b=[])
    assert not hasattr(b, '_b'), 'Set an underscore'


@async_test
async def test_backend_abstract_run_single():
    rules = Rules()
    rules._rules[RRType.TXT] = []
    rules._rules[RRType.A] = []

    async def pass_transparent(value):
        return value

    rules.process_record = pass_transparent

    b = BasicBackend()
    keys = iter(rules)
    async for result in b.run_single(rules, Domain('a')):
        assert result == next(keys), 'Failed to get the required result'


@async_test
async def test_backend_abstract_run():
    rules = Rules()
    rules._rules[RRType.CNAME] = []
    rules._rules[RRType.A] = []

    async def pass_transparent(value):
        return value

    rules.process_record = pass_transparent

    b = BasicBackend()

    from itertools import chain

    keys = chain(iter(rules), iter(rules))
    async for result in b.run(rules, Domain('a'), Domain('b')):
        assert result == next(keys), 'Failed to get the required result'


@async_test
async def test_backends_abstract_context_manager():
    calls = list()

    class CTXBackend(abstract.Backend):

        async def process(self, *_):
            calls.append('process')

        async def start(self):
            calls.append('start')

        async def stop(self):
            calls.append('stop')

    async with CTXBackend() as backend:
        assert calls == ['start'], 'Failed to call start'
        assert backend is not None, 'Failed to get a backend context'

    assert calls == ['start', 'stop'], 'Failed to call stop'
