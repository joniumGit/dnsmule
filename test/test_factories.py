from types import SimpleNamespace

import pytest

from dnsmule.rules.factories import add_default_factories, RuleFactoryMixIn


class DictWithName(dict):
    name = None


@pytest.mark.parametrize('factory_type', [
    'dns.regex',
    'dns.dynamic',
    ## Add more above
])
def test_factories_add_default_factories(factory_type):
    names = set()

    def assertion(type_name):
        names.add(type_name)
        return lambda o: o

    sn = SimpleNamespace(register=assertion)

    add_default_factories(sn)

    assert factory_type in names, 'Did not register factory'


def test_factories_mixin_passes_config():
    factory = RuleFactoryMixIn()
    definition = {}
    factory._factories['1'] = lambda **o: o
    assert factory.create_rule('1', definition) == {}, 'Did not pass config'


def test_factories_mixin_passes_non_empty_config():
    factory = RuleFactoryMixIn()
    definition = {'a': 1}
    factory._factories['1'] = lambda **o: o
    assert factory.create_rule('1', definition) == {'a': 1}, 'Did not pass config'


def test_factories_register():
    factory = RuleFactoryMixIn()

    @factory.register('test')
    def dummy():
        pass

    assert factory._factories['test'] is dummy, 'Failed to add factory'
