import pytest

from _async import async_test
from dnsmule.definitions import Record, Result, RRType
from dnsmule.rules import Rules, Rule


@pytest.fixture
def rules():
    yield Rules()


def dummy(_: Record) -> Result:
    pass


def test_rules_rule_name(rules):
    @rules.add.CNAME
    def my_cool_rule():
        pass

    assert "name='my_cool_rule'" in str(rules[RRType.CNAME].pop())


def test_rules_rule_unknown_type(rules):
    unknown = 65533

    def unknown_type(r: Record):
        return r.result()

    rules.add_rule(unknown, Rule(unknown_type))

    assert "name='unknown_type'" in str(rules[unknown].pop())


def test_rules_iter_returns_keys_from_rules(rules):
    marker = object()
    rules._rules[RRType.TXT] = marker

    assert next(iter(rules)) == RRType.TXT, 'Did not return the expected iteration result'


def test_rules_getitem_returns_items_from_rules(rules):
    marker = object()
    rules._rules[RRType.TXT] = marker

    assert rules[RRType.TXT] is marker, 'Did not return from rules'


def test_rules_length_returns_from_rules_values(rules):
    marker = object()
    rules._rules[RRType.TXT] = [marker, marker, marker]
    rules._rules[RRType.A] = [marker, marker, marker]

    assert len(rules) == 2, 'Did not return rule key count'


def test_rules_count_length_returns_from_rules_values(rules):
    marker = object()
    rules._rules[RRType.TXT] = [marker, marker, marker]
    rules._rules[RRType.A] = [marker, marker, marker]

    assert rules.rule_count() == 6, 'Did not return rule count'


def test_rules_getitem_returns_items_from_rules_conversion(rules):
    marker = object()
    rules._rules[RRType.A] = marker

    assert rules[1] is marker, 'Did not convert int'
    assert rules['a'] is marker, 'Did not convert lower string'
    assert rules['A'] is marker, 'Did not convert upper string'


def test_rules_get_types_returns_rules_keys(rules):
    marker = object()
    marker2 = object()

    rules._rules[marker] = 1
    rules._rules[marker2] = 2

    types = iter(rules.get_types())
    assert next(types) is marker, 'Unexpected return or order'
    assert next(types) is marker2, 'Unexpected return or order'


@async_test
async def test_rules_process_error(rules):
    class MockLog:

        def __getattr__(self, item):
            assert item == 'error', 'Unexpected attribute'
            return self.__call__

        def __call__(self, message, *args, **kwargs):
            assert len(args) == 0, 'Too many args'
            assert message is not None and isinstance(kwargs['exc_info'], ValueError), 'Arguments did not match'

    rules.log = MockLog()

    rules.add_rule(RRType.TXT, Rule(f=lambda *_, **__: exec('raise ValueError()')))

    res = await rules.process_record(Record(domain='example.com', data='', type=RRType.TXT))
    assert res is not None, 'Did not return result'
    assert not res, 'Did not return empty result'


@async_test
async def test_rules_process_async_rule(rules):
    class MockRule(Rule):
        called = set()

        def __call__(self, *args, **kwargs):
            self.called.add('__call__')
            return self

        def __getattr__(self, item):
            self.called.add(item)

        def __await__(self):
            self.called.add('__await__')

    rules.add_rule(RRType.TXT, MockRule())

    await rules.process_record(Record(domain='example.com', data='', type=RRType.TXT))

    assert MockRule.called == {'__call__', '__await__'}, 'Not all methods were called'


@async_test
async def test_rules_process_normal_rule(rules):
    class MockRule(Rule):
        called = set()

        def __call__(self, *args, **kwargs):
            self.called.add('__call__')
            return None

        def __getattr__(self, item):
            self.called.add(item)

        def __await__(self):
            assert False, 'Should not be called'

    rules.add_rule(RRType.MX, MockRule())

    await rules.process_record(Record(domain='example.com', data='', type=RRType.MX))

    assert MockRule.called == {'__call__'}, 'Not all or too many methods were called'
