import pytest

from dnsmule import RRType


@pytest.mark.parametrize('value,result', [
    ('1', 1),
    ('1', RRType.A),
    ('A', RRType.A),
    (1, RRType.A),
    (65530, 65530),
])
def test_unknown(value, result):
    assert RRType.from_any(value) == result, 'Produced unexpected result'


@pytest.mark.parametrize('value', [
    'testi',
    [],
    {},
    7000000,
    -1,
    1E5,
    '-1',
    '70000',
])
def test_bad_values_raise(value):
    with pytest.raises(Exception):
        RRType.from_any(value)
    with pytest.raises(Exception):
        RRType.from_text(value)
    with pytest.raises(Exception):
        RRType.to_text(value)


@pytest.mark.parametrize('value,text', [
    (RRType.A, 'A'),
    (1, 'A'),
    (RRType.ANY, 'ANY'),
    (255, 'ANY'),
    (65530, '65530'),
])
def test_to_text(value, text):
    assert RRType.to_text(value) == text


def test_to_str_and_repr():
    assert repr(RRType.A) == 'A'
    assert str(RRType.A) == 'A'
