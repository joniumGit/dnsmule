import pytest

from dnsmule.rules import Rules, Record, Result, Rule, Type, DynamicRule
from dnsmule.rules.utils import load_rules_from_config


@pytest.fixture
def rules():
    yield Rules()


def dummy(_: Record) -> Result:
    pass


def test_rules_rule_ordering():
    r0 = Rule(dummy, priority=0)
    r1 = Rule(dummy, priority=1)
    r2 = Rule(dummy, priority=2)

    data = [r2, r0, r1]
    data.sort()

    # priority is inverted
    assert data == [r2, r1, r0]


def test_rules_rule_ordering_with_changes():
    r0 = Rule(dummy, priority=0)
    r1 = Rule(dummy, priority=1)

    data = [r0, r1]
    data.sort()

    # priority is inverted
    assert data == [r1, r0]

    r1.priority = -1
    data.sort()

    # assert changes order
    assert data == [r0, r1]


def test_rules_rule_name(rules):
    @rules.add.CNAME
    def my_cool_rule():
        pass

    assert "name='my_cool_rule'" in str(rules[Type.CNAME].pop())


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

    load_rules_from_config([
        {
            'hello_world': None,
            'type': 'test',
            'record': 'TXT',
        }
    ], rules=rules)

    assert rules[Type.TXT].pop().f is dummy


def test_rules_dynamic_factory_operation(rules):
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

    load_rules_from_config([
        {
            'hello_world': None,
            'type': 'test',
            'record': 'TXT',
        }
    ], rules=rules)

    assert rules.process_record(Record(**dict(domain=None, type=Type.TXT, data=None))).tags[0] == 'True'


def test_create_regex_rule(rules):
    rule = rules.create_rule({
        'type': 'dns.regex',
        'name': 'test',
        'pattern': '^(test.)$',
        'attribute': '__str__',
        'group': 1,
        'flags': [
            'UNICODE',
            'DOTALL',
        ]
    })

    assert rule.f
    assert rule(Record(**dict(domain=None, type=Type.TXT, data='test\n'))).tags[0] == 'DNS::REGEX::TEST\n'
