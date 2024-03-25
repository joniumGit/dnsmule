import json

import pytest

from dnsmule import DoHBackend, RRType, Domain


@pytest.fixture
def mock_client():
    class Response:
        data = {
            "Status": 0,
            "TC": False,
            "RD": True,
            "RA": True,
            "AD": False,
            "CD": False,
            "Question": [
                {
                    "name": "example.com.",
                    "type": 1
                }
            ],
            "Answer": [
                {
                    "name": "example.com.",
                    "type": 1,
                    "TTL": 300,
                    "data": "127.0.0.1"
                }
            ],
            "Comment": "Response from 127.0.0.1."
        }

        def read(self):
            return json.dumps(self.data).encode()

        def close(self):
            return None

    class Mock:

        def request(self, *_, **__):
            return None

        def getresponse(self, *_, **__):
            return Response()

    yield Mock()


@pytest.fixture
def backend(mock_client):
    backend = DoHBackend(url='https://local')
    backend._client = mock_client
    yield backend


def test_doh_resolvers_domain_and_produces_result(backend):
    record = next(iter(backend.scan(Domain('example.com'), RRType.A)))
    assert record is not None


def test_doh_record_domain_no_trailing_dot(backend):
    record = next(iter(backend.scan(Domain('example.com'), RRType.A)))
    assert not record.name.endswith('.'), 'Record had trailing dot'


def test_doh_record_has_text_content(backend):
    record = next(iter(backend.scan(Domain('example.com'), RRType.A)))
    assert isinstance(record.text, str), 'Not text content'
