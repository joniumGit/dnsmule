import pytest

from dnsmule.definitions import RRType


@pytest.mark.parametrize('value,result', [
    ('RRType.of(1)', 1),
    ('RRType.of(1)', RRType.A),
])
def test_rrtype_unknown(value, result):
    assert RRType.from_any(value) == result, 'Produced unexpected result'


@pytest.mark.parametrize('value', [
    'testi',
    [],
    {},
    7000000,
    -1,
    1E5,
    'RRType.of(-1)',
    'RRType.of(70000)',
])
def test_rrtype_bad_values_raise(value):
    with pytest.raises(ValueError):
        RRType.from_any(value)
    with pytest.raises(ValueError):
        RRType.from_text(value)
    with pytest.raises(ValueError):
        RRType.to_text(value)


@pytest.mark.parametrize('value,text', [
    (RRType.A, 'A'),
    (1, 'A'),
    (RRType.ANY, 'ANY'),
    (255, 'ANY'),
    (65530, 'RRType.of(65530)'),
])
def test_rrtype_to_text(value, text):
    assert RRType.to_text(value) == text


def test_rrtype_eval_equals():
    assert eval('RRType.of(1)') == RRType.A, 'Did not equal enum member'
    assert eval('RRType.of(1)') is RRType.A, 'Did not meet enum "is" promise'


def test_rrtype_eval_unknown():
    assert eval('RRType.of(65530)') == 65530, 'Did not produce int'
