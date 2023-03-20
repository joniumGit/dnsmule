import random
import string
from typing import Callable, Any

import pytest

from dnsmule import Domain, RRType, Result, Record


class MockClosable:
    closed: bool = False

    def inherit(self, o: Any):
        self.__dict__.update({
            **o.__dict__,
            'close': self.close,
            'closed': self.closed,
        })

    def close(self):
        self.closed = True


class MockLogger:

    def __init__(self, ctx):
        self.result = []
        self.ctx = ctx

    def get_logger(self):
        return self

    def mock_in_module(self, module):
        self.ctx.setattr(module, 'get_logger', self.get_logger)

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
    yield lambda: generate_record().result


@pytest.fixture
def mock_closable():
    yield MockClosable()


def cached(f):
    from functools import wraps

    value = f()

    @wraps(f)
    def wrapper(*_, **__):
        return value

    return wrapper


pytest.cached = cached
