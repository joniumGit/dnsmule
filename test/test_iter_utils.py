import pytest

from dnsmule.utils import iter_utils


def test_iter_utils_iter_limit_short_iter():
    assert len(list(iter_utils.limit([1, 2, 3], n=4))) == 3, 'Short iter failed to limit to iter length'


def test_iter_utils_iter_limit_long_iter():
    assert len(list(iter_utils.limit([1, 2, 3, 4, 5], n=4))) == 4, 'Long iter was not limited correctly'


def test_iter_utils_iter_limit_exact_iter():
    assert len(list(iter_utils.limit([1, 2, 3, 4], n=4))) == 4, 'Did not return full iterable'


def test_iter_utils_sorter_return_item_value():
    # These are dict.items()
    assert iter_utils.sort_by_item_value(('key', 'value')) == 'value', 'Did not extract value from item'


@pytest.mark.parametrize('iterable,mapper,counts', [
    (
            [1, 2, 3, 4, 5],
            lambda o: o < 3,
            {
                True: 2,
                False: 3,
            }
    ),
    (
            ['a', 'b', 'c', 'aa', 'bb', 'cc'],
            lambda o: len(o),
            {
                1: 3,
                2: 3,
            }
    ),
    (
            ['a.b.c', 'a.c.d', 'r.b.c'],
            lambda o: o.split('.')[-3],
            {
                'a': 2,
                'r': 1,
            }
    ),
])
def test_iter_utils_count_by_function(iterable, mapper, counts):
    assert dict(iter_utils.count_by(iterable, mapper)) == counts, 'Unexpected counts output'


@pytest.mark.parametrize('reverse', (True, False))
def test_iter_utils_count_by_order(reverse):
    for value, expected in zip(
            sorted(
                [
                    ('a', 3),
                    ('b', 2),
                    ('c', 1),
                ],
                key=lambda t: t[1],
                reverse=reverse
            ),
            iter_utils.count_by(
                ['aa', 'bb', 'ab', 'ad', 'bc', 'ce'],
                lambda o: o[0],
                order='desc' if reverse else 'asc'
            )
    ):
        assert value == expected, 'Unexpected order'
