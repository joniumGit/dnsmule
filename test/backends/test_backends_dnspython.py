import pytest
from dns.exception import DNSException
from dns.message import make_query, from_text
from dns.rdatatype import RdataType

from dnsmule import Backend, RRType, Domain
from dnsmule.backends import dnspython
from dnsmule.backends.dnspython import DNSPythonBackend, message_to_record, DNSPythonRecord, default_query


@pytest.fixture(autouse=True)
def auto_fail_on_query(monkeypatch):
    with monkeypatch.context() as m:
        for key in DNSPythonBackend._SUPPORTED_QUERY_TYPES:
            m.setattr(
                dnspython,
                key if key != 'default' else 'udp_with_fallback',
                lambda *_, **__: pytest.fail('Called Disallowed Method'),
            )
            m.setitem(
                DNSPythonBackend._SUPPORTED_QUERY_TYPES,
                key,
                lambda *_, **__: pytest.fail('Called Disallowed Method'),
            )
        yield m


@pytest.fixture
def mock_query(monkeypatch):
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
            DNSPythonBackend._SUPPORTED_QUERY_TYPES,
            'default',
            udp_with_fallback_mock,
        )

        yield DefaultQuery


@pytest.mark.parametrize('fallback', [True, False])
def test_default_query_returns_single_value(mock_query, fallback):
    mock_query.fallback = fallback
    result = default_query(make_query('example.com', RdataType.A))
    assert result is mock_query.sentinel, 'Did not return sentinel value'


def test_default_query_logs_fallback(mock_query, logger):
    logger.mock_in_module(dnspython)
    mock_query.fallback = True
    default_query(make_query('example.com', RdataType.TXT))
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
    backend = DNSPythonBackend(querier=querier)
    assert backend._querier is not None, 'Failed to set querier'
    assert callable(backend._querier), 'Querier not callable'
    assert backend.querier == querier, 'Querier not set correctly'


def test_not_supported_querier_raises():
    with pytest.raises(ValueError):
        DNSPythonBackend(querier=object())


def test_backend_querier_defaults_to_default():
    backend = DNSPythonBackend()
    assert backend.querier == 'default', 'Failed to set default querier'
    assert backend._querier is not None, 'Failed to set default querier'


def test_resolver_defaults_to_something():
    backend = DNSPythonBackend()
    assert backend.resolver is not None, 'Failed to set resolver'


def test_resolver_is_accepted_as_kwarg():
    backend = DNSPythonBackend(resolver='33.33.33.33')
    assert backend.resolver == '33.33.33.33', 'Failed to set resolver from kwargs'


def test_resolver_defaults_to_system(monkeypatch):
    import dns.resolver as resolve

    resolver = resolve.Resolver()
    default = resolver.nameservers[0]

    backend = DNSPythonBackend()
    assert backend.resolver == default, 'Failed to set resolver to system default'


def test_message_to_record_empty_result_yields_nothing():
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
        next(iter(message_to_record(
            response,
        )))


def test_message_to_record_error_response_is_handled_gracefully():
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
        next(iter(message_to_record(
            response,
        )))


def test_message_to_record_returns_expected_class():
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
    record = next(iter(message_to_record(
        response,
    )))
    assert isinstance(record, DNSPythonRecord)


def test_message_to_record_handles_multiple_answers():
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
    record_iterator = iter(message_to_record(
        response,
    ))
    next(record_iterator)
    next(record_iterator)
    with pytest.raises(StopIteration):
        next(record_iterator)


def test_message_to_record_handles_additional_answers():
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
    record_iterator = iter(message_to_record(
        response,
    ))
    next(record_iterator)
    next(record_iterator)
    with pytest.raises(StopIteration):
        next(record_iterator)


def test_message_to_record_takes_type_from_response():
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
    record = next(iter(message_to_record(
        response,
    )))
    assert record.type == RRType.TXT


def test_message_to_record_takes_domain_from_response():
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
    record = next(iter(message_to_record(
        response,
    )))
    assert record.name == 'a.example.com'


def test_dnspython_record_text_property_returns_resource_record_content():
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
    record = next(iter(message_to_record(
        response,
    )))
    assert record.text == 'sentinel'


def test_dnspython_record_has_valid_text_representation():
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
    record = next(iter(message_to_record(
        response,
    )))
    assert record.text == '127.0.0.1'


def test_dnspython_implementation_record_attributes_are_accessible():
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
    record = next(iter(message_to_record(
        response,
    )))
    # Has dnspython attributes
    assert record.to_text() == '127.0.0.1'


def test_dnspython_dns_query_produces_a_record():
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
    backend = DNSPythonBackend()
    backend._querier = lambda *_, **__: response
    record = next(iter(backend.scan(
        Domain('example.com'),
        RRType.A,
    )))
    assert record is not None, 'Failed to produce response'


def test_dnspython_dns_query_empty_response_produces_no_records():
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
    backend = DNSPythonBackend()
    backend._querier = lambda *_, **__: response
    with pytest.raises(StopIteration):
        next(iter(backend.scan(
            Domain('example.com'),
            RRType.A,
        )))


def test_dnspython_dns_query_empty_record_types_yields_no_results():
    backend = DNSPythonBackend()
    backend._querier = lambda *_, **__: None
    with pytest.raises(StopIteration):
        next(iter(backend.scan(
            Domain('example.com'),
        )))


def test_dnspython_dns_query_error_handling_to_log(logger):
    logger.mock_in_module(dnspython)

    def timeout(*_, **__):
        raise DNSException()

    backend = DNSPythonBackend()
    backend._querier = timeout
    with pytest.raises(StopIteration):
        next(iter(backend.scan(
            Domain('example.com'),
            RRType.A,
        )))
    assert 'error' in logger.result, 'Failed to log result'


def test_backend_is_backend():
    assert issubclass(DNSPythonBackend, Backend), 'Did not inherit from backend'
