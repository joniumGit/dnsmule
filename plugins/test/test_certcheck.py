import datetime

import pytest

from dnsmule import Record, RRType
from dnsmule_plugins.certcheck import rule
from dnsmule_plugins.certcheck.certificates import Certificate


@pytest.fixture
def mock_collection(monkeypatch):
    with monkeypatch.context() as m:
        result = []
        m.setattr(rule.certificates, 'collect_certificates', lambda *_, **__: result)
        yield result


def test_certcheck_rule_creator_returns_callable():
    def dummy():
        pass

    creator = rule.CertChecker.creator(dummy)

    assert callable(creator), 'Failed to create callable'
    assert creator()._callback is dummy, 'Failed to bind callback'


def test_certcheck_call(mock_collection):
    check = rule.CertChecker()
    r = Record('', RRType.A, '')
    assert check(r)['resolvedCertificates'] == [], 'Failed to produce output'


def test_certcheck_call_add_domains(mock_collection):
    check = rule.CertChecker(ports=[443])
    r = Record('', RRType.A, '')

    cert1 = Certificate(
        version='v3',
        common='d.com',
        alts=['e.com'],
        valid_from=datetime.datetime.now(),
        valid_until=datetime.datetime.now(),
        issuer='',
    )

    cert2 = Certificate(
        version='v3',
        common='a.com',
        alts=['b.com'],
        valid_from=datetime.datetime.now(),
        valid_until=datetime.datetime.now(),
        issuer='',
    )

    r.result()['resolvedCertificates'] = [cert1.to_json()]
    mock_collection.append(cert2)

    assert check(r)['resolvedCertificates'] == [cert1.to_json(), cert2.to_json()], 'Failed to append data'


def test_certcheck_callback_with_domains(mock_collection):
    result = set()

    def callback(domains):
        result.update(domains)

    check = rule.CertChecker.creator(callback)(ports=[443], callback=True)

    r = Record('', RRType.A, '')

    cert1 = Certificate(
        version='v3',
        common='a.com',
        alts=['b.com'],
        valid_from=datetime.datetime.now(),
        valid_until=datetime.datetime.now(),
        issuer='',
    )
    mock_collection.append(cert1)

    check(r)

    assert result == {cert1.common, *cert1.alts}, 'Failed to contain all domains'
