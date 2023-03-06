import pytest

from _async import async_test
from dnsmule.backends.dnspython import DNSPythonBackend, _default_query


def test_backends_dnspython_default_query():
    import asyncio as aio
    assert aio.iscoroutinefunction(_default_query), 'Default query was not a coroutine'


@async_test
async def test_backends_dnspython_context_manager():
    async with DNSPythonBackend() as backend:
        assert backend is not None, 'Did not give instance for context manager'


@async_test
async def test_backend_dnspython_default_query_return(monkeypatch):
    marker = object()

    async def mock_query(*_, **__):
        return [marker, False]

    with monkeypatch.context() as ctx:
        from dnsmule.backends import dnspython
        ctx.setattr(dnspython, 'udp_with_fallback', mock_query)
        result = await _default_query(None)

    assert result is marker, 'Did not correctly propagate result'


@async_test
async def test_backend_dnspython_default_query_return_with_fallback(monkeypatch):
    marker = object()
    called = []

    async def mock_query(*_, **__):
        return [marker, True]

    class MockLogger:

        @staticmethod
        def debug(*_, **__):
            called.append('debug')

    def mock_logger():
        return MockLogger()

    with monkeypatch.context() as ctx:
        from dnsmule.backends import dnspython
        ctx.setattr(dnspython, 'udp_with_fallback', mock_query)
        ctx.setattr(dnspython, 'get_logger', mock_logger)
        result = await _default_query(None)

    assert result is marker, 'Did not correctly propagate result'
    assert called == ['debug'], 'Did not correctly call logger on fallback'


def test_backends_dnspython_bad_query_type():
    with pytest.raises(ValueError):
        DNSPythonBackend(querier='xxxxx')


def test_backends_dnspython_data_extensions(monkeypatch):
    from dnsmule.definitions import Data

    adapters = []

    def register_adapter(adapter):
        adapters.append(adapter)

    with monkeypatch.context() as ctx:
        ctx.setattr(Data, 'register_adapter', register_adapter)
        DNSPythonBackend.enable_data_extension()

    assert len(adapters) == 1, 'Did not register adapter'

    class MockItem:
        wow = object()

    class Mock:
        data = {
            'original': MockItem()
        }

    module_adapter = adapters[0]
    assert module_adapter(Mock(), 'wow') is MockItem.wow, 'Failed to get attribute'

    Mock.data.clear()
    assert module_adapter(Mock(), 'wow') is None, 'Got non-existent attribute'


@async_test
async def test_backends_dnspython_dns_query(monkeypatch):
    return_store = []

    async def mock_query(*_, **__):
        return [return_store.pop(), False]

    with monkeypatch.context() as ctx:
        from dnsmule.backends import dnspython
        ctx.setattr(dnspython, 'udp_with_fallback', mock_query)
        backend = DNSPythonBackend()

        marker = object()
        return_store.append(marker)
        results = [o async for o in backend.dns_query('example.com', 1)]

        assert len(results) == 1, 'Failed to produce result'
        assert results[0] is marker, 'Failed to produce correct result'


@async_test
async def test_backends_dnspython_dns_query_timeout(monkeypatch):
    called = []

    class MockLogger:

        @staticmethod
        def error(*_, **__):
            called.append('error')

        @staticmethod
        def debug(*_, **__):
            called.append('debug')

    def mock_logger():
        return MockLogger()

    async def mock_query(*_, **__):
        from dns.exception import Timeout
        raise Timeout()

    with monkeypatch.context() as ctx:
        from dnsmule.backends import dnspython
        ctx.setattr(dnspython, 'udp_with_fallback', mock_query)
        ctx.setattr(dnspython, 'get_logger', mock_logger)
        backend = DNSPythonBackend()

        results = [o async for o in backend.dns_query('example.com', 1)]
        assert len(results) == 0, 'Produced result even with timeout'
        assert called == ['debug', 'error'], 'Failed to log timeout'


@async_test
async def test_backends_dnspython_process():
    from dns.rdatatype import RdataType
    backend = DNSPythonBackend()
    marker = object()

    class MockTarget:
        name = object()

    async def yield_transparent_query(name, *types):
        assert name is MockTarget.name, 'Wrong name'
        assert types == tuple(RdataType.make(i) for i in range(1, 4, 1)), 'Failed to get right types'
        yield marker

    def yield_transparent_process(target, message):
        assert target.name is MockTarget.name, 'Wrong target'
        assert message is marker, 'Wrong message'
        yield message

    backend._process_message = yield_transparent_process
    backend.dns_query = yield_transparent_query

    results = [o async for o in backend.process(MockTarget(), 1, 2, 3)]
    assert results[0] is marker, 'Wrong result'


def test_backends_dnspython_process_message():
    from dns.rdatatype import RdataType
    from dnsmule.definitions import RRType, Record

    backend = DNSPythonBackend()

    class MockRecord:
        rdtype = RdataType.A

        @staticmethod
        def to_text():
            return '""aaa IN bbb"'

    class MockMessage:
        answer = [[MockRecord()]]

    marker = 'a'
    result: Record = [*backend._process_message(marker, MockMessage())][0]

    assert isinstance(result, Record), '[result Result]'
    assert result.domain.name == marker, 'Wrong domain'
    assert result.type == RRType.A, 'Wrong result type'
    assert result.data.value == '"aaa IN bbb', 'Wrong result value or failed to strip'
    assert 'original' in result.data, 'Failed to add extended data'
