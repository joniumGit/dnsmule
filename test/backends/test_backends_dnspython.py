import pytest
from dns.exception import DNSException
from dns.message import make_query, from_text
from dns.rdatatype import RdataType

from dnsmule import Backend, RRType, Domain
from dnsmule.backends import dnspython


@pytest.fixture
def reload():
    import importlib
    yield lambda: importlib.reload(dnspython)


@pytest.fixture(autouse=True)
def auto_fail_on_query(monkeypatch):
    with monkeypatch.context() as m:
        for key in dnspython.DNSPythonBackend._SUPPORTED_QUERY_TYPES:
            m.setattr(
                dnspython,
                key if key != 'default' else 'udp_with_fallback',
                lambda *_, **__: pytest.fail('Called Disallowed Method'),
            )
            m.setitem(
                dnspython.DNSPythonBackend._SUPPORTED_QUERY_TYPES,
                key,
                lambda *_, **__: pytest.fail('Called Disallowed Method'),
            )
        yield m


@pytest.fixture
def default_query(monkeypatch):
    class DefaultQuery:
        sentinel = object()
        fallback = False

    def udp_with_fallback_mock(*_, **__):
        return [DefaultQuery.sentinel, DefaultQuery.fallback]

    with monkeypatch.context() as m:
        m.setattr(
            dnspython,
            'udp_with_fallback',
            udp_with_fallback_mock,
        )
        m.setitem(
            dnspython.DNSPythonBackend._SUPPORTED_QUERY_TYPES,
            'default',
            udp_with_fallback_mock,
        )

        yield DefaultQuery


@pytest.mark.parametrize('fallback', [True, False])
def test_default_query_returns_single_value(default_query, fallback):
    default_query.fallback = fallback
    result = dnspython.default_query(make_query('example.com', RdataType.A))
    assert result is default_query.sentinel, 'Did not return sentinel value'


def test_default_query_logs_fallback(default_query, logger):
    logger.mock_in_module(dnspython)
    default_query.fallback = True
    dnspython.default_query(make_query('example.com', RdataType.TXT))
    assert logger.result == ['debug'], 'Did not correctly call logger on fallback'


@pytest.mark.parametrize('querier', [
    'https',
    'quic',
    'tls',
    'tcp',
    'udp',
    'default',
])
def test_supported_queriers(querier):
    backend = dnspython.DNSPythonBackend(querier=querier)
    assert backend._querier is not None, 'Failed to set querier'
    assert callable(backend._querier), 'Querier not callable'
    assert backend.querier == querier, 'Querier not set correctly'


def test_not_supported_querier_raises():
    with pytest.raises(ValueError):
        dnspython.DNSPythonBackend(querier=object())


def test_backend_defaults():
    backend = dnspython.DNSPythonBackend()
    assert backend.querier == 'default', 'Failed to set default querier'
    assert backend._querier is not None, 'Failed to set default querier'


def test_resolver_defaults_to_something():
    backend = dnspython.DNSPythonBackend()
    assert backend.resolver is not None, 'Failed to set resolver'


def test_resolver_defaults_to_env(monkeypatch, reload):
    resolver = '0.0.0.0'
    with monkeypatch.context() as m:
        m.setenv('DNSMULE_DEFAULT_RESOLVER', resolver)
        reload()
        backend = dnspython.DNSPythonBackend()
    assert backend.resolver == resolver, 'Failed to set resolver'


def test_message_to_record_empty_yields_nothing():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    with pytest.raises(StopIteration):
        next(iter(dnspython.message_to_record(
            response,
        )))


def test_message_to_record_error_is_ok():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode SERVFAIL'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    with pytest.raises(StopIteration):
        next(iter(dnspython.message_to_record(
            response,
        )))


def test_message_to_record_correct_class():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\nexample.com. 2563 IN A 127.0.0.1'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record = next(iter(dnspython.message_to_record(
        response,
    )))
    assert isinstance(record, dnspython.DNSPythonRecord)


def test_message_to_record_multiple():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\nexample.com. 2563 IN A 127.0.0.1'
        '\nexample.com. 2563 IN A 127.0.0.2'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record_iterator = iter(dnspython.message_to_record(
        response,
    ))
    next(record_iterator)
    next(record_iterator)
    with pytest.raises(StopIteration):
        next(record_iterator)


def test_message_to_record_multiple_from_additional():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\nexample.com. 2563 IN A 127.0.0.1'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
        '\nexample.com. 2563 IN A 127.0.0.2'
    )
    record_iterator = iter(dnspython.message_to_record(
        response,
    ))
    next(record_iterator)
    next(record_iterator)
    with pytest.raises(StopIteration):
        next(record_iterator)


def test_message_to_record_correct_type():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN TXT'
        '\n;ANSWER'
        '\nexample.com. 2563 IN TXT "a"'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record = next(iter(dnspython.message_to_record(
        response,
    )))
    assert record.type == RRType.TXT


def test_message_to_record_correct_domain():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN TXT'
        '\n;ANSWER'
        '\na.example.com. 2563 IN TXT "a"'  # Different from query
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record = next(iter(dnspython.message_to_record(
        response,
    )))
    assert record.domain == 'a.example.com'


def test_dnspython_record_text():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN TXT'
        '\n;ANSWER'
        '\nexample.com. 2563 IN TXT "sentinel"'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record = next(iter(dnspython.message_to_record(
        response,
    )))
    assert record.text == 'sentinel'


def test_dnspython_record_text_ip():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\nexample.com. 2563 IN A 127.0.0.1'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record = next(iter(dnspython.message_to_record(
        response,
    )))
    assert record.text == '127.0.0.1'


def test_dnspython_record_attrs():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\nexample.com. 2563 IN A 127.0.0.1'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    record = next(iter(dnspython.message_to_record(
        response,
    )))
    # Has dnspython attributes
    assert record.to_text() == '127.0.0.1'


def test_dnspython_dns_query():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\nexample.com. 2563 IN A 127.0.0.1'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    backend = dnspython.DNSPythonBackend()
    backend._querier = lambda *_, **__: response
    record = next(iter(backend.single(
        Domain('example.com'),
        RRType.A,
    )))
    assert record is not None, 'Failed to produce response'


def test_dnspython_dns_query_empty_response():
    response = from_text(
        'id 54307'
        '\nopcode QUERY'
        '\nrcode NOERROR'
        '\nflags QR RD RA'
        '\n;QUESTION'
        '\nexample.com. IN A'
        '\n;ANSWER'
        '\n;AUTHORITY'
        '\n;ADDITIONAL'
    )
    backend = dnspython.DNSPythonBackend()
    backend._querier = lambda *_, **__: response
    with pytest.raises(StopIteration):
        next(iter(backend.single(
            Domain('example.com'),
            RRType.A,
        )))


def test_dnspython_dns_query_empty_types():
    backend = dnspython.DNSPythonBackend()
    backend._querier = lambda *_, **__: None
    with pytest.raises(StopIteration):
        next(iter(backend.single(
            Domain('example.com'),
        )))


def test_dnspython_dns_query_timeout(logger):
    logger.mock_in_module(dnspython)

    def timeout(*_, **__):
        raise DNSException()

    backend = dnspython.DNSPythonBackend()
    backend._querier = timeout
    with pytest.raises(StopIteration):
        next(iter(backend.single(
            Domain('example.com'),
            RRType.A,
        )))
    assert 'error' in logger.result, 'Failed to log result'


def test_backend_is_backend():
    assert issubclass(dnspython.DNSPythonBackend, Backend), 'Did not inherit from backend'
