import pytest

from dnsmule.utils.baseclasses import *


class ValueComparable(Comparable, KwargClass):
    value: int

    def __lt__(self, other):
        return self.value < other.value


@pytest.fixture
def class_with_property():
    class PropertyTarget:
        backing = object()

        @classproperty
        def value(cls):
            return cls.backing

    yield PropertyTarget


def test_get_classproperty_from_instance(class_with_property):
    target = class_with_property()
    assert target.value == target.backing, 'Failed to match value'


def test_get_classproperty_from_class(class_with_property):
    assert class_with_property.value == class_with_property.backing, 'Failed to match value'


def test_set_classproperty_fails_on_instance(class_with_property):
    with pytest.raises(AttributeError):
        class_with_property().value = 20


def test_del_classproperty_fails_on_instance(class_with_property):
    with pytest.raises(AttributeError):
        del class_with_property().value
    assert class_with_property.value == class_with_property.backing, 'Failed to retain value'


def test_set_classproperty_overrides_on_class(class_with_property):
    class_with_property.value = 20
    assert class_with_property().value == 20, 'Failed to set value'


def test_del_classproperty_overrides_on_class(class_with_property):
    del class_with_property.value
    assert not hasattr(class_with_property(), 'value'), 'Failed to delete value'


def test_comparable_sort_comparable():
    values = [
        ValueComparable(value=1),
        ValueComparable(value=3),
        ValueComparable(value=2),
    ]
    values.sort()
    assert list(map(lambda o: o.value, values)) == [1, 2, 3]


def test_comparable_lt_only():
    a = ValueComparable(value=1)
    b = ValueComparable(value=2)
    c = ValueComparable(value=3)

    assert a < b < c


def test_comparable_subclass_works():
    class ComparableSubclass(ValueComparable):
        pass

    a = ComparableSubclass(value=1)
    b = ComparableSubclass(value=2)
    c = ComparableSubclass(value=3)

    assert a < b < c


def test_comparable_no_impl_throws():
    class NoImpl(Comparable):
        """Doesn't implement required methods
        """

    with pytest.raises(TypeError):
        NoImpl()


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
        _id = 'a'

    assert A.id == 'a', 'Failed to use _id'


def test_identifiable_no_id():
    class B(Identifiable):
        pass

    assert B.id is not None, 'Failed to have default id'
