import json
from contextlib import contextmanager
from typing import List, Dict, Callable
from urllib.request import urlopen, Request

from ..iprange import IPvXRange


class Providers:
    _mapping: Dict[str, Callable[[], List[IPvXRange]]] = {}

    @staticmethod
    def all() -> List[str]:
        return [*Providers._mapping.keys()]

    @staticmethod
    def fetch(provider: str) -> List[IPvXRange]:
        return Providers._mapping[provider]()

    @staticmethod
    def available(provider: str) -> bool:
        return provider in Providers._mapping

    @staticmethod
    def register(provider: str) -> Callable[[Callable[[], List[IPvXRange]]], Callable[[], List[IPvXRange]]]:
        def handle_registration(f):
            Providers._mapping[provider] = f
            return f

        return handle_registration


@contextmanager
def grab(url: str, add_agent: bool = False):
    with urlopen(Request(
            url=url,
            headers={'User-Agent': 'DNSMule IPRanges Plugin'} if add_agent else {},
    ), timeout=2) as f:
        yield f


def fetch_json(url: str, **kwargs) -> dict:
    with grab(url, **kwargs) as f:
        return json.load(f)


def fetch_text(url: str, **kwargs) -> str:
    with grab(url, **kwargs) as f:
        return f.read().decode('utf-8')


__all__ = [
    'Providers',
    'IPvXRange',
    'fetch_text',
    'fetch_json',
]
