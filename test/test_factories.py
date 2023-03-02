from types import SimpleNamespace

import pytest

from dnsmule.rules.factories import add_default_factories, RuleFactoryMixIn


@pytest.mark.parametrize('factory_type', [
    'dns.regex',
    'dns.dynamic',
    ## Add more above
])
def test_foctories_add_default_factories(factory_type):
    names = set()

    def assertion(type_name):
        names.add(type_name)
        return lambda o: o

    sn = SimpleNamespace(register=assertion)

    add_default_factories(sn)

    assert factory_type in names, 'Did not register factory'


def test_factories_mixin_pops_type():
    factory = RuleFactoryMixIn()
    definition = {'type': '1'}
    factory._factories['1'] = lambda **o: o
    assert factory.create_rule(definition) == {}, 'Did not pop type'


def test_factories_mixin_passes_kwargs():
    factory = RuleFactoryMixIn()
    definition = {'type': '1', 'a': 1}
    factory._factories['1'] = lambda **o: o
    assert factory.create_rule(definition) == {'a': 1}, 'Did not pass kwargs'


def test_factories_register():
    factory = RuleFactoryMixIn()

    @factory.register('test')
    def dummy():
        pass

    assert factory._factories['test'] is dummy, 'Failed to add factory'
