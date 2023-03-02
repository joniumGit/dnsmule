import pytest

from _async import async_test
from dnsmule.definitions import Record, Result, RRType
from dnsmule.rules import Rules, Rule, DynamicRule
from dnsmule.rules.utils import load_rules


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


def test_rules_factory_operation(rules):
    @rules.register('test')
    def my_cool_rule(name: str, **__):
        assert name == 'hello_world'
        return Rule(dummy)

    load_rules([
        {
            'hello_world': None,
            'type': 'test',
            'record': 'TXT',
        }
    ], rules=rules)

    assert rules[RRType.TXT].pop().f is dummy


@async_test
async def test_rules_dynamic_factory_operation(rules):
    from textwrap import dedent

    @rules.register('test')
    def my_cool_rule(name: str, **__):
        assert name == 'hello_world'
        return DynamicRule(code=dedent(
            # language=Python
            """
            GLOBAL_DATA = {}
            
            def init():
                GLOBAL_DATA['init'] = True
            
            def process(record):
                assert GLOBAL_DATA['init']
                return record.identify(str(GLOBAL_DATA['init']))
            """
        ))

    load_rules([
        {
            'hello_world': None,
            'type': 'test',
            'record': 'TXT',
        }
    ], rules=rules)

    result = await rules.process_record(Record(domain='example.com', type=RRType.TXT, data='data'))
    assert next(iter(result.tags)) == 'True'


def test_create_regex_rule(rules):
    rule = rules.create_rule({
        'type': 'dns.regex',
        'name': 'test',
        'pattern': '(test.)',
        'attribute': '__str__',
        'group': 1,
        'flags': [
            'UNICODE',
            'DOTALL',
        ]
    })

    assert rule.f

    res = rule(Record(domain='example.com', type=RRType.TXT, data='test\n'))
    assert next(iter(res.tags)) == 'DNS::REGEX::TEST::TEST\n'
