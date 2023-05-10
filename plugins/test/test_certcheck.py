import datetime

import pytest

from dnsmule import Record, RRType, Result, Domain
from dnsmule_plugins.certcheck import rule
from dnsmule_plugins.certcheck.certificates import Certificate


@pytest.fixture
def mock_collection(monkeypatch):
    with monkeypatch.context() as m:
        result = []
        m.setattr(rule.certificates, 'collect_certificates', lambda *_, **__: result)
        yield result


def test_rule_creator_returns_callable():
    def dummy():
        pass

    creator = rule.CertChecker.creator(dummy)

    assert callable(creator), 'Failed to create callable'
    assert creator()._callback is dummy, 'Failed to bind callback'


def test_call(mock_collection):
    check = rule.CertChecker()
    r = Record(Domain(''), RRType.A, '')
    assert 'resolvedCertificates' not in check(r).data, 'Added key without data to add'


def test_call_adds_key(mock_collection):
    mock_collection.append(Certificate(
        version='v3',
        common='a.com',
        alts=['b.com'],
        valid_from=datetime.datetime.now(),
        valid_until=datetime.datetime.now(),
        issuer='',
    ))
    check = rule.CertChecker()
    r = Record(Domain(''), RRType.A, '')
    assert 'resolvedCertificates' in check(r).data, 'Failed to add key'


def test_call_add_certs(mock_collection):
    check = rule.CertChecker(ports=[443])
    r = Record(Domain(''), RRType.A, '')
    r.existing = Result(Domain(''))

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

    r.existing.data['resolvedCertificates'] = [cert1.to_json()]
    mock_collection.append(cert2)
    mock_collection.append(cert1)

    result = check(r)

    assert len((check(r)).data['resolvedCertificates']) == 2, 'Failed to remove duplicates'

    certs = result.data['resolvedCertificates']
    assert cert1 in certs, 'Failed to append existing data'
    assert cert2 in certs, 'Failed to append data'

    assert len((check(r)).data['resolvedCertificates']) == 2, 'Failed to remove duplicates'


def test_callback_with_domains(mock_collection):
    result = set()

    def callback(*domains):
        result.update(domains)

    check = rule.CertChecker.creator(callback)(ports=[443], callback=True)

    r = Record(Domain(''), RRType.A, '')

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
