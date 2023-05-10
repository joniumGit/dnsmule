from dnsmule.baseclasses import *


def test_kwarg_class_repr():
    kw = KwargClass(a=1, b=2, c='yyy')
    assert repr(kw) == 'KwargClass(a=1,b=2,c=\'yyy\')', 'Failed to get desired repr'


def test_kwarg_class_str_eq_repr():
    kw = KwargClass(a=1, b=2)
    assert repr(kw) == str(kw), 'Failed to get same repr'


def test_kwarg_class_repr_eval():
    kw = KwargClass(a=1, b='c')
    kw2 = eval(repr(kw))
    assert kw2.a == kw.a, 'Failed to persist'
    assert kw2.b == kw.b, 'Failed to persist'


def test_kwarg_class_subclass_repr_eval():
    class AClass(KwargClass):
        a: int
        b: str

    kw = AClass(a=1, b='c')
    kw2 = eval(repr(kw))

    assert repr(KwargClass(a=1, b='c')) != repr(kw)
    assert kw2.a == kw.a, 'Failed to persist'
    assert kw2.b == kw.b, 'Failed to persist'


def test_identifiable_id():
    class A(Identifiable):
        id = 'a'

    assert A.id == 'a', 'Failed to use _id'


def test_identifiable_no_id():
    class B(Identifiable):
        pass

    assert B.id is not None, 'Failed to have default id'
