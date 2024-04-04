import datetime

from dnsmule import Result, Domain, RRType
from dnsmule_plugins.certcheck.adapter import save_result, load_result
from dnsmule_plugins.certcheck.certificates import Certificate

test_cert = Certificate(
    version='2',
    common='example.com',
    issuer='test',
    valid_from=datetime.datetime.now(),
    valid_until=datetime.datetime.now(),
    alts=[],
)


def test_saving():
    result = Result(Domain('example.com'), [RRType.TXT])
    result.data['resolvedCertificates'] = {test_cert}
    result = save_result(result)
    assert result.data['resolvedCertificates'] == [test_cert.to_json()]


def test_loading():
    result = Result(Domain('example.com'), [RRType.TXT])
    result.data['resolvedCertificates'] = [test_cert.to_json()]
    result = load_result(result)
    assert result.data['resolvedCertificates'] == {test_cert}


def test_saving_no_key():
    result = Result(Domain('example.com'), [RRType.TXT])
    result = save_result(result)
    assert 'resolvedCertificates' not in result.data, 'Added key when not present'


def test_loading_no_key():
    result = Result(Domain('example.com'), [RRType.TXT])
    result = load_result(result)
    assert 'resolvedCertificates' not in result.data, 'Added key when not present'
