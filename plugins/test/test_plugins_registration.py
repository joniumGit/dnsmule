from dnsmule import DNSMule
from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule_plugins import *


def test_ip_ranges():
    mule = DNSMule.make()
    IPRangesPlugin().register(mule)
    assert 'ip.ranges' in mule.rules._factories


def test_certcheck():
    mule = DNSMule.make()
    CertCheckPlugin().register(mule)
    assert 'ip.certs' in mule.rules._factories


def test_certcheck_callback_ok():
    mule = DNSMule.make()
    CertCheckPlugin(callback=True).register(mule)
    assert 'ip.certs' in mule.rules._factories


def test_ptrs():
    mule = DNSMule.make(backend=DNSPythonBackend())
    PTRScanPlugin().register(mule)
    assert 'ip.ptr' in mule.rules._factories
