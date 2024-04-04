import datetime

import pytest

from dnsmule import Result, Domain
from dnsmule_plugins.certcheck import rule
from dnsmule_plugins.certcheck.certificates import Certificate


@pytest.fixture
def mock_collection(monkeypatch):
    with monkeypatch.context() as m:
        result = []
        m.setattr(rule.certificates, 'collect_certificates', lambda *_, **__: result)
        yield result


def test_call(mock_collection, record, result):
    check = rule.CertChecker()
    check(record, result)
    assert 'resolvedCertificates' not in result.data, 'Added key without data to add'


def test_call_adds_key(mock_collection, record, result):
    mock_collection.append(Certificate(
        version='v3',
        common='a.com',
        alts=['b.com'],
        valid_from=datetime.datetime.now(),
        valid_until=datetime.datetime.now(),
        issuer='',
    ))
    check = rule.CertChecker()
    check(record, result)
    assert 'resolvedCertificates' in result.data, 'Failed to add key'


def test_call_add_certs(mock_collection, record, result):
    check = rule.CertChecker(ports=[443])
    record.existing = Result(Domain(''))

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

    record.existing.data['resolvedCertificates'] = [cert1.to_json()]
    mock_collection.append(cert2)
    mock_collection.append(cert1)

    check(record, result)
    check(record, result)

    assert len(result.data['resolvedCertificates']) == 2, 'Failed to remove duplicates'

    certs = result.data['resolvedCertificates']
    assert cert1.to_json() in certs, 'Failed to append existing data'
    assert cert2.to_json() in certs, 'Failed to append data'

    check(record, result)

    assert len(result.data['resolvedCertificates']) == 2, 'Failed to remove duplicates'
