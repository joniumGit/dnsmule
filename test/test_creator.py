import pytest

from dnsmule.definitions import RRType, Record, Result
from dnsmule.rules.entities import RuleCreator, Rule


class Assertions:
    rule: Rule

    def __init__(self):
        self.store = {}

    def assert_from_rule(self, **kwargs):

        def callback(rtype, rule):
            if 'type' in kwargs:
                assert rtype == kwargs.pop('type'), 'RRType did not match'
            for k, v in kwargs.items():
                assert getattr(rule, k) == v, 'Attribute mismatch'
            self.store['rule'] = rule

        return callback

    @staticmethod
    def fail():

        def callback(*_):
            assert False, 'Should not get here'

        return callback

    def __getattr__(self, item):
        return self.store[item]


@pytest.fixture
def assertions():
    yield Assertions()


def dummy(_: Record) -> Result:
    pass


def test_creator_callback_gets_called(assertions):
    c = RuleCreator(
        callback=assertions.assert_from_rule(type=RRType.A),
        type='A',
        priority=0,
    )

    assert c(dummy) is dummy, 'Rule creation callback failed'


def test_creator_callback_throws_without_type(assertions):
    c = RuleCreator(callback=assertions.fail(), priority=1, type=None)

    with pytest.raises(ValueError):
        c(dummy)


def test_creator_set_priority(assertions):
    c = RuleCreator(callback=assertions.fail(), priority=None, type=None)
    c = c[10]
    assert c.priority == 10, 'Priority did not apply'


def test_creator_set_priority_only_once(assertions):
    c = RuleCreator(callback=assertions.fail(), priority=None, type=None)
    c = c[10]

    with pytest.raises(ValueError):
        _ = c[20]


def test_creator_set_type(assertions):
    c = RuleCreator(callback=assertions.fail(), type=None, priority=None)
    c = c.TXT
    assert c.type == 'TXT', 'Type did not apply'


def test_creator_set_type_only_once(assertions):
    c = RuleCreator(callback=assertions.fail(), type=None, priority=None)
    c = c.TXT

    with pytest.raises(ValueError):
        _ = c.MX


def test_creator_defaults(assertions):
    c = RuleCreator(callback=assertions.fail())

    assert c.type is None, 'Type was not none'
    assert c.priority is None, 'Priority was not none'


def test_creator_defaults_to_zero_priority(assertions):
    c = RuleCreator(callback=assertions.assert_from_rule(priority=Rule.priority), type='TXT')

    assert c.priority is None, 'Priority was not none'
    assert c(dummy) is dummy, 'Bad return'
