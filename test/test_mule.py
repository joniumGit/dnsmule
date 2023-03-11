from pathlib import Path
from typing import AsyncGenerator, Any

import pytest

from _async import async_test
from dnsmule import DNSMule, RRType
from dnsmule.backends.abstract import Backend
from dnsmule.backends.noop import NOOPBackend
from dnsmule.definitions import Domain, Record, Result
from dnsmule.loader import Config, Initializer
from dnsmule.plugins.noop import NOOPPlugin
from dnsmule.rules import Rules, Rule


class SimpleBackend(Backend):
    o: Any

    async def process(self, target: Domain, *types: RRType) -> AsyncGenerator[Record, Any]:
        yield self.o


def test_mule_load_simple():
    mule = DNSMule.load(Path(__file__).parent / 'sample_1.yml')
    assert type(mule.backend) == NOOPBackend, 'Failed to create correct backend'


def test_mule_with_existing_backend_and_rules():
    rules = Rules()
    mule = DNSMule.make(rules=rules, backend=SimpleBackend())
    assert type(mule.backend) == SimpleBackend, 'Failed to persist backend'
    assert mule.rules is rules, 'Failed to persist rules'


def test_mule_with_existing_backend_and_rules_from_file():
    rules = Rules()
    mule = DNSMule(file=Path(__file__).parent / 'sample_1.yml', rules=rules, backend=SimpleBackend())
    assert type(mule.backend) == SimpleBackend, 'Failed to persist backend'
    assert mule.rules is rules, 'Failed to persist rules'


def test_mule_nones():
    with pytest.raises(ValueError):
        DNSMule(rules=None)
    with pytest.raises(ValueError):
        DNSMule(backend=None)
    with pytest.raises(ValueError):
        DNSMule()


@async_test
async def test_mule_swap_backend():
    mule = DNSMule.load(Path(__file__).parent / 'sample_1.yml')
    assert type(mule.backend) == NOOPBackend, 'Failed to create correct backend'
    await mule.swap_backend(SimpleBackend())
    assert type(mule.backend) == SimpleBackend, 'Failed to swap backend'


@async_test
async def test_mule_context_manager():
    calls = list()

    class CTXBackend(Backend):

        async def process(self, *_):
            calls.append('process')

        async def start(self):
            calls.append('start')

        async def stop(self):
            calls.append('stop')

    async with DNSMule.make(rules=Rules(), backend=CTXBackend()) as backend:
        assert calls == ['start'], 'Failed to call start'
        assert backend is not None, 'Failed to get a backend context'

    assert calls == ['start', 'stop'], 'Failed to call stop'


def test_mule_len_data():
    mule = DNSMule.make(Rules(), NOOPBackend())
    assert len(mule) == 0, 'Was not 0 len at creation'
    mule.store_domains('a', 'b')
    assert len(mule) == 2, 'Was not length of domains'


def test_mule_domains_sorted():
    mule = DNSMule.make(Rules(), NOOPBackend())
    mule.store_domains('c', 'g')
    mule.store_domains('a', 'e')
    assert mule.domains() == ['a', 'c', 'e', 'g'], 'Failed to generate domains ordered'


def test_mule_contains_domain_and_str():
    mule = DNSMule.make(Rules(), NOOPBackend())
    mule.store_domains('a')
    assert 'b' not in mule, 'Returned True for data that does not exist'
    assert 'a' in mule, 'Did not contain data'
    assert Domain('a') in mule, 'Did not match Domain'


def test_mule_getitem_no_data():
    data = DNSMule.make(Rules(), NOOPBackend())['abg']
    assert data is None, 'Returned something from key that does not exist'


def test_mule_getitem_with_data():
    mule = DNSMule.make(Rules(), NOOPBackend())
    mule.store_domains('a')

    result = mule['a']
    assert len(result) == 0, 'Returned non-empty result'

    result = mule[Domain('a')]
    assert len(result) == 0, 'Returned non-empty result'


def test_mule_store_same_domain_same_length():
    mule = DNSMule.make(Rules(), NOOPBackend())
    mule.store_domains('a')
    assert len(mule) == 1, 'Failed to add domain'
    mule.store_domains('a')
    assert len(mule) == 1, 'Length changed on adding the same domain'


def test_mule_append_rules():
    mule = DNSMule.make(Rules(), NOOPBackend())
    assert len(mule.rules) == 0, 'Rules not empty'
    mule.append_config(Path(__file__).parent / 'sample_2.yml')
    assert len(mule.rules) != 0, 'Rules still empty'


def test_mule_add_result():
    mule = DNSMule.make(Rules(), NOOPBackend())
    assert len(mule) == 0, 'Mule not empty on creation'
    mule.store_result(Result(domain=Domain('a')))
    assert len(mule) == 1, 'Mule did not store result'
    mule.store_result(Result(domain=Domain('a')))
    assert len(mule) == 1, 'Mule did not append result'


@async_test
async def test_mule_run_adds_domains():
    mule = DNSMule.make(Rules(), NOOPBackend())
    assert len(mule) == 0, 'Mule not empty on creation'
    await mule.run('a')
    assert len(mule) == 1, 'Mule did not store domain'


@async_test
async def test_mule_run_adds_domains():
    rules = Rules()

    async def pass_transparent(o):
        return o

    rules.process_record = pass_transparent

    mule = DNSMule.make(rules, SimpleBackend())

    r = Result(Domain('a'))
    r.tags.add('abcd')

    mule.backend.o = r

    assert len(mule) == 0, 'Mule not empty on creation'
    await mule.run('a')

    assert len(mule) == 1, 'Mule did not store domain'
    assert mule['a'].tags == {'abcd'}, 'Failed to add result'


def test_mule_duplicate_rule_throws():
    m = DNSMule.make(Rules(), SimpleBackend())
    m.rules.add_rule(RRType.TXT, Rule(lambda: None, name='regex_test'))
    with pytest.raises(ValueError):
        m.append_config(Path(__file__).parent / 'sample_2.yml')


def test_mule_duplicate_rule_name_different_record_ok():
    m = DNSMule.make(Rules(), SimpleBackend())
    m.rules.add_rule(65535, Rule(lambda: None, name='regex_test'))
    m.append_config(Path(__file__).parent / 'sample_2.yml')
    assert sum(map(len, m.rules.values())) == 2, 'Did not match rule count'


def test_mule_add_rule_with_existing_record_ok():
    m = DNSMule.make(Rules(), SimpleBackend())
    m.rules.add_rule(RRType.TXT, Rule(lambda: None, name='regex_test_2'))
    m.append_config(Path(__file__).parent / 'sample_2.yml')
    assert sum(map(len, m.rules.values())) == 2, 'Did not match rule count'


def test_mule_backend_type_name():
    m = DNSMule.make(Rules(), SimpleBackend())
    assert m.backend_type == 'SimpleBackend', 'Failed to get type name for backend'


def test_mule_add_existing_plugin_does_not_call_init():
    m = DNSMule.make(Rules(), SimpleBackend())
    called_count = [0]

    class FalseNoopPlugin(NOOPPlugin):
        @property
        def type(self):
            return type(self).__name__

        def register(self, _):
            called_count[0] += 1

    m._append_plugins(Config(plugins=[Initializer(type='noop', f=FalseNoopPlugin)], backend=None, rules=None))
    assert 'noop' in m.plugins, 'Did not add plugin'
    assert called_count[0] == 1, 'Did not call register'

    m._append_plugins(Config(plugins=[Initializer(type='noop', f=FalseNoopPlugin)], backend=None, rules=None))
    assert called_count[0] == 1, 'Called the plugin registration again'
