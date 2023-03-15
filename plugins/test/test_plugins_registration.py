from dnsmule import DNSMule
from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.backends.noop import NOOPBackend
from dnsmule_plugins import *


def test_plugins_registration_ip_ranges():
    mule = DNSMule.make()
    IPRangesPlugin().register(mule)
    assert 'ip.ranges' in mule.rules._factories


def test_plugins_registration_certcheck():
    mule = DNSMule.make()
    CertCheckPlugin().register(mule)
    assert 'ip.certs' in mule.rules._factories


def test_plugins_registration_certcheck_callback_ok():
    mule = DNSMule.make()
    CertCheckPlugin(callback=True).register(mule)
    assert 'ip.certs' in mule.rules._factories


def test_plugins_registration_ptrs_skips_on_bad_backend():
    mule = DNSMule.make(backend=NOOPBackend())
    PTRScanPlugin().register(mule)
    assert 'ip.ptr' not in mule.rules._factories


def test_plugins_registration_ptrs():
    mule = DNSMule.make(backend=DNSPythonBackend())
    PTRScanPlugin().register(mule)
    assert 'ip.ptr' in mule.rules._factories
