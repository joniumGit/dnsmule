from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dnsmule import DNSMule, Plugin
from dnsmule.definitions import Result, Domain, RRType
from dnsmule.storages.kvstorage import result_to_json_data
from server import app

test_rules = Path(__file__).parent / 'rules.yml'


@pytest.fixture(scope='function')
def mule():
    mule = DNSMule.load(test_rules)
    yield mule


@pytest.fixture(scope='function')
def client(mule, monkeypatch):
    client = TestClient(app)
    client.app.state.mule = mule
    yield client
    del client.app.state.mule


def test_server_startup(monkeypatch):
    with monkeypatch.context() as m:
        import server
        m.setattr(server, 'rules', test_rules)
        with TestClient(app) as tc:
            assert tc.app.state.mule is not None, 'Failed to initialize mule'


def test_server_get_results_empty(client):
    r = client.get('/results')
    assert r.status_code == 200, 'Failed call'
    assert r.json()['results'] == [], 'Results not empty'


def test_server_get_results_items(client, mule):
    result = Result(
        initial_type=RRType.A,
        domain=Domain('example.com')
    )
    result.tag('test_tag')
    result.data['test_data'] = 1
    mule.storage[result.domain] = result

    r = client.get('/results')
    assert r.status_code == 200, 'Failed to find results'
    assert r.json() == {
        'results': [
            result_to_json_data(result),
        ]
    }, 'Result output was different'


def test_server_scan_domain(client):
    r = client.post('/scan?domain=a.example.com')
    assert r.status_code == 202, 'Failed to start processing'

    r = client.get('/results')
    assert r.status_code == 200, 'Failed to find results'
    assert r.json()['results'][0]['domain'] == 'a.example.com', 'Failed to show in results'


def test_server_scan_domain_single_result(client):
    r = client.post('/scan?domain=c.example.com')
    assert r.status_code == 202, 'Failed to start processing'

    r = client.get('/results?domain=c.example.com')
    assert r.status_code == 200, 'Failed to find result'
    assert r.json()['domain'] == 'c.example.com', 'Failed to show in results'


def test_server_results_get_non_existing(client):
    r = client.get('/results?domain=b.example.com')
    assert r.status_code == 404, 'Failed to indicate scan does not exists'


def test_server_get_rules(client):
    r = client.get('/rules')
    assert r.status_code == 200, 'Failed to get rules'
    assert r.json() == {
        'A': [
            'test_rule_1',
            'test_rule_2',
        ],
        '65530': [
            'test_rule_1',
        ],
    }


def test_server_get_rules_empty_type(client, mule):
    # Clears rules and adds a default if not exists
    mule.rules._rules.clear()
    mule.rules._rules[RRType.A] = []
    assert len(mule.rules._rules.keys()) != 0, 'No data'

    r = client.get('/rules')
    assert r.status_code == 200, 'Failed to get rules'
    assert r.json() == {}, 'Produced rules with content'


def test_server_delete_rules_by_name(client):
    r = client.delete('/rules?name=test_rule_1')
    assert r.status_code == 204, 'Failed to delete'
    r = client.get('/rules')
    assert r.status_code == 200, 'Failed to get rules'
    assert r.json() == {
        'A': [
            'test_rule_2',
        ],
    }


def test_server_delete_rules_by_type_and_name(client):
    r = client.delete('/rules?name=test_rule_1&record=A')
    assert r.status_code == 204, 'Failed to delete'
    r = client.get('/rules')
    assert r.status_code == 200, 'Failed to get rules'
    assert r.json() == {
        'A': [
            'test_rule_2',
        ],
        '65530': [
            'test_rule_1',
        ],
    }


def test_server_rescan_count(client):
    client.post('/scan?domain=example.com')
    client.post('/scan?domain=a.example.com')

    r = client.post('/rescan')
    assert r.status_code == 202, 'Failed to start processing'
    assert r.headers['scan-count'] == '2', 'Failed to re-scan all data'


def test_server_rescan_count_empty(client):
    r = client.post('/rescan')
    assert r.status_code == 202, 'Failed to start processing'
    assert r.headers['scan-count'] == '0', 'Actually re-scanned something'


def test_server_create_new_rule_duplicate(client, mule):
    assert mule.rules.contains(RRType.A, 'test_rule_1'), 'Failed to have seed data'
    r = client.post('/rules', json={
        'type': 'dns.regex',
        'record': 'A',
        'name': 'test_rule_1',
        'config': {
            'pattern': 'a',
        },
    })
    assert r.status_code == 409, 'Failed to prevent duplicate'


def test_server_create_new_rule(client, mule):
    mule.rules._rules.clear()
    r = client.post('/rules', json={
        'type': 'dns.regex',
        'record': 'A',
        'name': 'test_rule_3',
        'config': {
            'pattern': 'a',
        },
    })
    assert r.status_code == 201, 'Failed to create rule'
    assert client.get('/rules').json()['A'][0] == 'test_rule_3', 'Failed to append to rules'


def test_server_get_plugins(client, mule):
    class Plugin1(Plugin):
        _id = 'test_plugin_1'

        def register(self, _):
            """Never called
            """

    mule.plugins.add(Plugin1())
    r = client.get('/plugins')
    assert r.status_code == 200, 'Failed call'
    assert r.json() == {
        'plugins': [
            'test_plugin_1',
        ]
    }


def test_server_create_new_rule_invalid_type(client, mule):
    r = client.post('/rules', json={
        'type': 'dns.regex',
        'record': 'STRING',
        'name': 'test_rule_1',
        'config': {
            'pattern': 'a',
        },
    })
    assert r.status_code == 422, 'Failed to prevent bad types'


def test_server_delete_rules_by_type_and_name_invalid_type(client):
    r = client.delete('/rules?name=test_rule_1&record=STRING::QDq')
    assert r.status_code == 422, 'Failed to prevent invalid query'


def test_server_delete_rules_by_type_and_name_not_exists(client, mule):
    mule.rules._rules.clear()
    r = client.delete('/rules?name=test_rule_1')
    assert r.status_code == 404, 'Failed to indicate missing rules'


def test_server_create_new_rule_invalid_rule_type(client, mule):
    mule.rules._rules.clear()
    r = client.post('/rules', json={
        'type': '[object Object]',
        'record': 'A',
        'name': 'test_rule_1',
        'config': {
            'pattern': 'a',
        },
    })
    assert r.status_code == 404, 'Failed to indicate missing rule type'


def test_server_create_new_rule_rule_failure(client, mule):
    mule.rules._rules.clear()
    r = client.post('/rules', json={
        'type': 'dns.regex',
        'record': 'A',
        'name': 'test_rule_1',
        'config': {
            'pattern': 123,
        },
    })
    assert r.status_code == 400, 'Failed to indicate rule error'
    assert len(r.json()['detail']), 'Failed to give all details'
