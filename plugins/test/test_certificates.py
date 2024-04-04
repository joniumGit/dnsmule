import os
import socket
import ssl
import sys
from textwrap import dedent
from types import SimpleNamespace
from typing import Any

import pytest

from dnsmule_plugins.certcheck import certificates

NO_CRYPTOGRAPHY = os.system('python -c "import cryptography"')
EXAMPLE_ADDRESS = certificates.Address(family=socket.AF_INET, tuple=('', 0))
SAMPLE_CERTS = [
    dedent(
        """
        -----BEGIN CERTIFICATE-----
        MIIFKDCCBM6gAwIBAgIQC9JZWvfkeVKsGBwPw1rxijAKBggqhkjOPQQDAjBKMQsw
        CQYDVQQGEwJVUzEZMBcGA1UEChMQQ2xvdWRmbGFyZSwgSW5jLjEgMB4GA1UEAxMX
        Q2xvdWRmbGFyZSBJbmMgRUNDIENBLTMwHhcNMjIxMDE4MDAwMDAwWhcNMjMxMDE3
        MjM1OTU5WjByMQswCQYDVQQGEwJVUzETMBEGA1UECBMKQ2FsaWZvcm5pYTEWMBQG
        A1UEBxMNU2FuIEZyYW5jaXNjbzEZMBcGA1UEChMQQ2xvdWRmbGFyZSwgSW5jLjEb
        MBkGA1UEAxMSb25kaWdpdGFsb2NlYW4uYXBwMFkwEwYHKoZIzj0CAQYIKoZIzj0D
        AQcDQgAEG2J2Mkx1pbnMhx86dX07Wm5B/AS7nu6sBQF/jVsS4mFM921Jyvs0VkY1
        6mjd/sya1UniE67v0hU3Bm7Agz3wiqOCA2wwggNoMB8GA1UdIwQYMBaAFKXON+rr
        sHUOlGeItEX62SQQh5YfMB0GA1UdDgQWBBTwtTLhT9RIInPJ2O8wgf3L8w1YUTAz
        BgNVHREELDAqghJvbmRpZ2l0YWxvY2Vhbi5hcHCCFCoub25kaWdpdGFsb2NlYW4u
        YXBwMA4GA1UdDwEB/wQEAwIHgDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUH
        AwIwewYDVR0fBHQwcjA3oDWgM4YxaHR0cDovL2NybDMuZGlnaWNlcnQuY29tL0Ns
        b3VkZmxhcmVJbmNFQ0NDQS0zLmNybDA3oDWgM4YxaHR0cDovL2NybDQuZGlnaWNl
        cnQuY29tL0Nsb3VkZmxhcmVJbmNFQ0NDQS0zLmNybDA+BgNVHSAENzA1MDMGBmeB
        DAECAjApMCcGCCsGAQUFBwIBFhtodHRwOi8vd3d3LmRpZ2ljZXJ0LmNvbS9DUFMw
        dgYIKwYBBQUHAQEEajBoMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdpY2Vy
        dC5jb20wQAYIKwYBBQUHMAKGNGh0dHA6Ly9jYWNlcnRzLmRpZ2ljZXJ0LmNvbS9D
        bG91ZGZsYXJlSW5jRUNDQ0EtMy5jcnQwDAYDVR0TAQH/BAIwADCCAX0GCisGAQQB
        1nkCBAIEggFtBIIBaQFnAHYArfe++nz/EMiLnT2cHj4YarRnKV3PsQwkyoWGNOvc
        gooAAAGD621qbQAABAMARzBFAiAq/9p/XhHp0ze8wB9FGH/kAcvWWa6zIbw2Mrgs
        BKRvZAIhAIgEjRPSTrgp1rJh8B5BVnFh49PLsO7QB2YWMWgKw2r3AHUAs3N3B+GE
        UPhjhtYFqdwRCUp5LbFnDAuH3PADDnk2pZoAAAGD621qYgAABAMARjBEAiAF7pOX
        CSyzZzI3vUEd6RdtgvQDrajsXlXYEkWzVlIr3AIgGvtUx6cR9jtRGhA1dCeoqS+X
        IjtThubFKzPlke7cRQkAdgC3Pvsk35xNunXyOcW6WPRsXfxCz3qfNcSeHQmBJe20
        mQAAAYPrbWowAAAEAwBHMEUCIQDi/0ilqEur3PhRvpia+OZd6kXU//jUgB8Co9Aj
        UihYOAIgMPrdZr0yOz2LKrQD6I5YKmgRafnm7oyEtySAYOqki9IwCgYIKoZIzj0E
        AwIDSAAwRQIhANOy4eAzudci/3h2VoEoOboscJJSkUu/54A7gqF1tNdpAiB0pNHU
        biUPQMCvLXuL2J2QhjbvfklJObDsrmNh1uO3nA==
        -----END CERTIFICATE-----
        -----BEGIN CERTIFICATE-----
        MIIDzTCCArWgAwIBAgIQCjeHZF5ftIwiTv0b7RQMPDANBgkqhkiG9w0BAQsFADBa
        MQswCQYDVQQGEwJJRTESMBAGA1UEChMJQmFsdGltb3JlMRMwEQYDVQQLEwpDeWJl
        clRydXN0MSIwIAYDVQQDExlCYWx0aW1vcmUgQ3liZXJUcnVzdCBSb290MB4XDTIw
        MDEyNzEyNDgwOFoXDTI0MTIzMTIzNTk1OVowSjELMAkGA1UEBhMCVVMxGTAXBgNV
        BAoTEENsb3VkZmxhcmUsIEluYy4xIDAeBgNVBAMTF0Nsb3VkZmxhcmUgSW5jIEVD
        QyBDQS0zMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEua1NZpkUC0bsH4HRKlAe
        nQMVLzQSfS2WuIg4m4Vfj7+7Te9hRsTJc9QkT+DuHM5ss1FxL2ruTAUJd9NyYqSb
        16OCAWgwggFkMB0GA1UdDgQWBBSlzjfq67B1DpRniLRF+tkkEIeWHzAfBgNVHSME
        GDAWgBTlnVkwgkdYzKz6CFQ2hns6tQRN8DAOBgNVHQ8BAf8EBAMCAYYwHQYDVR0l
        BBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMBIGA1UdEwEB/wQIMAYBAf8CAQAwNAYI
        KwYBBQUHAQEEKDAmMCQGCCsGAQUFBzABhhhodHRwOi8vb2NzcC5kaWdpY2VydC5j
        b20wOgYDVR0fBDMwMTAvoC2gK4YpaHR0cDovL2NybDMuZGlnaWNlcnQuY29tL09t
        bmlyb290MjAyNS5jcmwwbQYDVR0gBGYwZDA3BglghkgBhv1sAQEwKjAoBggrBgEF
        BQcCARYcaHR0cHM6Ly93d3cuZGlnaWNlcnQuY29tL0NQUzALBglghkgBhv1sAQIw
        CAYGZ4EMAQIBMAgGBmeBDAECAjAIBgZngQwBAgMwDQYJKoZIhvcNAQELBQADggEB
        AAUkHd0bsCrrmNaF4zlNXmtXnYJX/OvoMaJXkGUFvhZEOFp3ArnPEELG4ZKk40Un
        +ABHLGioVplTVI+tnkDB0A+21w0LOEhsUCxJkAZbZB2LzEgwLt4I4ptJIsCSDBFe
        lpKU1fwg3FZs5ZKTv3ocwDfjhUkV+ivhdDkYD7fa86JXWGBPzI6UAPxGezQxPk1H
        goE6y/SJXQ7vTQ1unBuCJN0yJV0ReFEQPaA1IwQvZW+cwdFD19Ae8zFnWSfda9J1
        CZMRJCQUzym+5iPDuI9yP+kHyCREU3qzuWFloUwOxkgAyXVjBYdwRVKD05WdRerw
        6DEdfgkfCv4+3ao8XnTSrLE=
        -----END CERTIFICATE-----
        """
    ).strip(),
    {'subject': (
        (('countryName', 'US'),), (('stateOrProvinceName', 'California'),), (('localityName', 'San Francisco'),),
        (('organizationName', 'Cloudflare, Inc.'),), (('commonName', 'ondigitalocean.app'),)), 'issuer': (
        (('countryName', 'US'),), (('organizationName', 'Cloudflare, Inc.'),),
        (('commonName', 'Cloudflare Inc ECC CA-3'),)), 'version': 3, 'serialNumber': '0BD2595AF7E47952AC181C0FC35AF18A',
        'notBefore': 'Oct 18 00:00:00 2022 GMT', 'notAfter': 'Oct 17 23:59:59 2023 GMT',
        'subjectAltName': (('DNS', 'ondigitalocean.app'), ('DNS', '*.ondigitalocean.app')),
        'OCSP': ('http://ocsp.digicert.com',), 'caIssuers': ('http://cacerts.digicert.com/CloudflareIncECCCA-3.crt',),
        'crlDistributionPoints': (
            'http://crl3.digicert.com/CloudflareIncECCCA-3.crl', 'http://crl4.digicert.com/CloudflareIncECCCA-3.crl')},
]


@pytest.fixture
def mock_cert_cryptography(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(ssl, 'get_server_certificate', lambda *_, **__: SAMPLE_CERTS[0])

        yield


@pytest.fixture
def mock_cert_stdlib(monkeypatch):
    with monkeypatch.context() as m:
        m.setattr(ssl.SSLSocket, 'getpeercert', lambda *_, **__: SAMPLE_CERTS[1])
        m.setattr(ssl.SSLSocket, 'connect', lambda *_, **__: None)

        yield


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
def test_collect_certificate_return(cert: Any, result):
    assert certificates.resolve_domain_from_certificate(cert) == result


@pytest.mark.skipif(NO_CRYPTOGRAPHY, reason='No cryptography installed')
def test_collect_certs_same_result(mock_cert_cryptography, mock_cert_stdlib):
    c1 = certificates.collect_certificate(EXAMPLE_ADDRESS, timeout=.5)
    c2 = certificates.collect_certificate(EXAMPLE_ADDRESS, prefer_stdlib=False, timeout=.5)
    assert c1 == c2


@pytest.mark.skipif(NO_CRYPTOGRAPHY, reason='No cryptography installed')
def test_collect_certs_crypto_no_extension(mock_cert_cryptography, monkeypatch):
    from cryptography.x509.extensions import ExtensionNotFound, ExtensionOID, Extensions

    def dummy(*_, **__):
        raise ExtensionNotFound('test', ExtensionOID.SUBJECT_ALTERNATIVE_NAME)

    with monkeypatch.context() as m:
        m.setattr(Extensions, 'get_extension_for_oid', dummy)
        c = certificates.collect_certificate(EXAMPLE_ADDRESS, prefer_stdlib=False, timeout=.5)

    assert len(c.alts) == 0, 'Failed'


def test_collect_error_none():
    c1 = certificates.collect_certificate_stdlib(EXAMPLE_ADDRESS, timeout=.1)
    c2 = certificates.collect_certificate_cryptography(EXAMPLE_ADDRESS, timeout=.1)
    c3 = certificates.collect_certificate(EXAMPLE_ADDRESS, timeout=.1)
    assert c1 is c2 is c3 is None


def test_massage_handles_falsy():
    assert certificates.massage_certificate_stdlib({}) is None
    assert certificates.massage_certificate_stdlib(None) is None


def test_import_error(monkeypatch):
    with monkeypatch.context() as m:
        m.setitem(sys.modules, 'cryptography', None)
        m.setattr(certificates, 'collect_certificate_cryptography', None)
        cert = certificates.collect_certificate(EXAMPLE_ADDRESS, prefer_stdlib=False)
    assert cert is None, 'Failed to pass on exception'


def test_import_error_2(monkeypatch):
    def thrower(*_, **__):
        raise ImportError()

    class FailLogger:

        def __init__(self, *_):
            pass

        @staticmethod
        def warning(*o):
            pytest.fail(repr(o))

    with monkeypatch.context() as m:
        m.setattr(ssl, 'get_server_certificate', thrower)
        m.setattr(certificates, 'getLogger', FailLogger)
        cert = certificates.collect_certificate_cryptography(EXAMPLE_ADDRESS, 1.)
    assert cert is None, 'Failed to pass on exception'


def test_collect_certificates(monkeypatch, mock_cert_stdlib):
    with monkeypatch.context() as m:
        m.setattr(socket, 'getaddrinfo', lambda *_, **__: [
            (
                socket.AF_INET,
                ...,
                ...,
                ...,
                EXAMPLE_ADDRESS.tuple,
            )
        ])
        certs = certificates.collect_certificates(*EXAMPLE_ADDRESS.tuple)

    assert len(certs) == 1, 'Failed to call get certificate'


def test_collect_none(monkeypatch, mock_cert_stdlib):
    with monkeypatch.context() as m:
        m.setattr(socket, 'getaddrinfo', lambda *_, **__: [
            (
                socket.AF_INET,
                ...,
                ...,
                ...,
                EXAMPLE_ADDRESS.tuple,
            )
        ])
        m.setitem(globals(), 'SAMPLE_CERTS', [None, None])

        certs = certificates.collect_certificates(*EXAMPLE_ADDRESS.tuple)

    assert len(certs) == 0, 'Failed to skip none value'


def test_collect_raising_gets_empty(monkeypatch):
    def dummy(*_, **__):
        raise socket.error()

    with monkeypatch.context() as m:
        m.setattr(socket, 'getaddrinfo', dummy)

        certs = certificates.collect_certificates(*EXAMPLE_ADDRESS.tuple)

    assert len(certs) == 0, 'Failed to pass exceptions'
