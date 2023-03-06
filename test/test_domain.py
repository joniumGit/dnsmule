import pytest

from dnsmule.definitions import Domain


def test_domain_str_equals_domain_name():
    d = Domain('example.com')
    assert str(d) == d.name, 'Domain did not equal string form'


def test_domain_repr_create_simple():
    d = Domain('example.com')
    d1 = eval(repr(d))
    assert d1.name == d.name, 'Domain names not equal'
    assert d1 == d, 'Domains not equal'


def test_domain_repr_create_kwargs():
    d = Domain('example.com', a='b', c=1)
    d1 = eval(repr(d))
    assert d1.name == d.name, 'Domain names not equal with kwargs'
    assert d1 == d, 'Domains not equal with kwargs'


def test_domain_equals_and_hash_with_domain():
    d1 = Domain('example.com', a='b', c=1)
    d2 = Domain('example.com')
    assert d1 == d2, 'Domains not equal with kwargs'
    assert hash(d1) == hash(d2), 'Domain hashes not equal with kwargs'


def test_domain_equals_and_hash_with_str():
    d1 = Domain('example.com', a='b', c=1)
    d2 = 'example.com'
    assert d1 == d2, 'Domain not equal to string form'
    assert hash(d1) == hash(d2), 'Domain hash not equal to string form'


@pytest.mark.parametrize('a,b,r', [
    ('a.b.c', Domain('a.b.d'), False),
    ('d.a.b.c', Domain('a.b.c'), False),
    ('c.d', Domain('b.c.d'), True),
    ('c.d', 'b.c.d', True),
    ('d', 'c', False),
])
def test_domain_subdomain_functionality(a, b, r):
    assert Domain(a).is_subdomain(b) == r, 'Unexpected subdomain result'


def test_domain_is_comparable():
    assert list(sorted([Domain('c'), Domain('x'), Domain('a')])) == ['a', 'c', 'x'], 'Unexpected sort order'


def test_domain_from_domain():
    assert Domain(Domain('a')).name == 'a', 'Retained wrapping'
