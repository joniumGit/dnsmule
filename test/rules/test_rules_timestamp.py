import pytest

from dnsmule import Record, Domain, RRType, Result, TimestampRule


@pytest.fixture
def record():
    yield Record(
        name=Domain('example.com'),
        type=RRType.A,
        data='127.0.0.1',
    )


@pytest.fixture
def result():
    yield Result(
        name=Domain('example.com'),
    )


def test_timestamp_rule_adds_to_data(record, result):
    rule = TimestampRule()

    with rule:
        rule(record, result)

    assert 'last_scan' in result.data
    assert 'scans' in result.data


def test_timestamp_rule_appends_to_scans(record, result):
    rule = TimestampRule()

    result.data['scans'] = [None]

    with rule:
        rule(record, result)

    assert len(result.data['scans']) == 2, 'Failed to append scan'


def test_timestamp_rule_does_not_append_twice(record, result):
    rule = TimestampRule()

    result.data['scans'] = []

    with rule:
        rule(record, result)
        rule(record, result)

    assert len(result.data['scans']) == 1
