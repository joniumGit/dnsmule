from dataclasses import dataclass

import pytest

from dnsmule.utils import Comparable


@dataclass
class ValueComparable(metaclass=Comparable, key='value', reverse=False):
    value: int


@dataclass
class ValueComparableReversed(metaclass=Comparable, key='value', reverse=True):
    value: int


def test_comparable_sort_comparables():
    values = [
        ValueComparable(value=1),
        ValueComparable(value=3),
        ValueComparable(value=2),
    ]
    values.sort()
    assert list(map(lambda o: o.value, values)) == [1, 2, 3]


def test_comparable_sort_reversed_comparables():
    values = [
        ValueComparableReversed(value=1),
        ValueComparableReversed(value=3),
        ValueComparableReversed(value=2),
    ]
    values.sort()
    assert list(map(lambda o: o.value, values)) == [3, 2, 1]


def test_comparable_rich_methods():
    a = ValueComparable(value=1)
    b = ValueComparable(value=2)
    c = ValueComparable(value=3)

    assert a <= b <= c
    assert c >= b >= a
    assert a < b < c
    assert c > b > a
    assert b >= a


def test_comparable_subclass_works():
    class ComparableSubclass(ValueComparable):
        pass

    a = ComparableSubclass(value=1)
    b = ComparableSubclass(value=2)
    c = ComparableSubclass(value=3)

    assert a <= b <= c
    assert c >= b >= a
    assert a < b < c
    assert c > b > a
    assert b >= a


def test_comparable_no_args_throws():
    with pytest.raises(ValueError) as e:
        class _(metaclass=Comparable):
            pass

    assert 'compare by' in e.value.args[0]


def test_comparable_does_not_define_extra_attrs():
    with pytest.raises(AttributeError):
        ValueComparable(1).name
    with pytest.raises(AttributeError):
        ValueComparableReversed(1).name
