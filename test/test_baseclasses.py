import pytest

from dnsmule.utils import KwargClass, Comparable


class ValueComparable(Comparable, KwargClass):
    value: int

    def __lt__(self, other):
        return self.value < other.value


def test_baseclasses_comparable_sort_comparable():
    values = [
        ValueComparable(value=1),
        ValueComparable(value=3),
        ValueComparable(value=2),
    ]
    values.sort()
    assert list(map(lambda o: o.value, values)) == [1, 2, 3]


def test_baseclasses_comparable_lt_only():
    a = ValueComparable(value=1)
    b = ValueComparable(value=2)
    c = ValueComparable(value=3)

    assert a < b < c


def test_baseclasses_comparable_subclass_works():
    class ComparableSubclass(ValueComparable):
        pass

    a = ComparableSubclass(value=1)
    b = ComparableSubclass(value=2)
    c = ComparableSubclass(value=3)

    assert a < b < c


def test_baseclasses_comparable_no_impl_throws():
    class NoImpl(Comparable):
        """Doesn't implement required methods
        """

    with pytest.raises(TypeError):
        NoImpl()


def test_baseclasses_kwarg_class_repr():
    kw = KwargClass(a=1, b=2, c='yyy')
    assert repr(kw) == 'KwargClass(a=1,b=2,c=\'yyy\')', 'Failed to get desired repr'


def test_baseclasses_kwarg_class_str_eq_repr():
    kw = KwargClass(a=1, b=2)
    assert repr(kw) == str(kw), 'Failed to get same repr'


def test_baseclasses_kwarg_class_repr_eval():
    kw = KwargClass(a=1, b='c')
    kw2 = eval(repr(kw))
    assert kw2.a == kw.a, 'Failed to persist'
    assert kw2.b == kw.b, 'Failed to persist'
