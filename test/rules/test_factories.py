import pytest

from dnsmule import Rule
from dnsmule.rules.factories import RuleFactoryMixIn


class DictWithName(dict):
    name = None


@pytest.mark.parametrize('factory_type', [
    'dns.regex',
    'dns.dynamic',
    # Add more above
])
def test_factories_add_default_factories(factory_type):
    rf = RuleFactoryMixIn()
    assert factory_type in rf._factories, 'Did not register factory'


def test_factories_mixin_passes_config():
    factory = RuleFactoryMixIn()
    definition = {}
    factory._factories['1'] = lambda **o: o
    assert factory.create('1', definition) == {}, 'Did not pass config'


def test_factories_mixin_passes_non_empty_config():
    factory = RuleFactoryMixIn()
    definition = {'a': 1}
    factory._factories['1'] = lambda **o: o
    assert factory.create('1', definition) == {'a': 1}, 'Did not pass config'


def test_factories_register():
    factory = RuleFactoryMixIn()

    @factory.register('test')
    def dummy():
        pass

    assert factory._factories['test'] is dummy, 'Failed to add factory'


def test_factories_register_not_a_rule():
    factory = RuleFactoryMixIn()

    class A:
        pass

    with pytest.raises(TypeError):
        factory.register(A)


def test_factories_register_a_rule():
    factory = RuleFactoryMixIn()

    class A(Rule):
        _id = 'test.rule'

    factory.register(A)

    assert 'test.rule' in factory._factories, 'Failed to add rule'


def test_factories_register_a_rule_type_returns_type():
    factory = RuleFactoryMixIn()

    class A(Rule):
        _id = 'test.rule'

    assert factory.register(A) == A
