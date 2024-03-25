import random
import string
from typing import Callable

import pytest

from dnsmule import Domain, RRType, Result, Record


class MockLogger:

    def __init__(self, ctx):
        self.result = []
        self.ctx = ctx

    def get_logger(self, _):
        return self

    def mock_in_module(self, module):
        self.ctx.setattr(module, 'getLogger', self.get_logger)

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        self.result.append(item)
        return lambda *_, **__: None


@pytest.fixture(autouse=True, scope='function')
def logger(monkeypatch):
    with monkeypatch.context() as m:
        yield MockLogger(m)


@pytest.fixture
def generate_record() -> Callable[[], Record]:
    def generate():
        choices = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters + '-'
        prefix = ''.join(random.choices(choices, k=random.randint(1, 63)))
        domain = Domain(
            prefix
            + '.'
            + ''.join(random.choices(choices, k=random.randint(1, 64 - len(prefix))))
        )
        return Record(domain, random.choice([*RRType]), ''.join(random.choices(choices, k=100)))

    yield generate


@pytest.fixture
def generate_result(generate_record) -> Callable[[], Result]:
    def generate():
        record = generate_record()
        return Result(
            name=record.name,
            types={record.type},
            tags=[],
            data={},
        )

    yield generate
