import socket
from types import SimpleNamespace

import pytest

from dnsmule_plugins.certcheck import certificates

EXAMPLE_ADDRESS = certificates.Address(family=socket.AF_INET, tuple=('example', 443))


@pytest.mark.parametrize('cert,result', [
    (None, []),
    (SimpleNamespace(
        common='common.common',
        alts=[
            'alt.common',
            'alt2.common',
        ]
    ), [
         'common.common',
         'alt.common',
         'alt2.common',
     ])
])
def test_certificates_collect_certificate_return(cert, result):
    assert certificates.resolve_domain_from_certificate(cert) == result


def test_certificates_collect_certs_same_result():
    c1 = certificates.collect_certificate(EXAMPLE_ADDRESS)
    c2 = certificates.collect_certificate(EXAMPLE_ADDRESS, prefer_stdlib=False)
    assert c1 == c2


def test_certificates_collect_error_none():
    c1 = certificates.collect_certificate_stdlib(EXAMPLE_ADDRESS, 1)
    c2 = certificates.collect_certificate_cryptography(EXAMPLE_ADDRESS, 1)
    c3 = certificates.collect_certificate(EXAMPLE_ADDRESS)
    assert c1 is c2 is c3 is None


def test_certificates_massage_handles_falsy():
    assert certificates.massage_certificate_stdlib({}) is None
    assert certificates.massage_certificate_stdlib(None) is None


def test_certificates_import_failure(monkeypatch):
    import sys

    with monkeypatch.context() as m:
        m.setitem(sys.modules, 'cryptography', None)

        with pytest.raises(ImportError) as e:
            certificates.collect_certificate(EXAMPLE_ADDRESS, prefer_stdlib=False)

    assert 'halted' in e.value.args[0]
