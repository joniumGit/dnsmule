from typing import Callable, Any, Dict, List

from .rrtype import RRType


class Data:
    type: RRType
    value: str
    data: Dict[str, any]
    _adapters: List[Callable[['Data'], Any]] = []

    # noinspection PyShadowingBuiltins
    def __init__(self, type: RRType, value: str, **kwargs):
        self.type = type
        self.value = value
        self.data = {**kwargs}

    def to_text(self):
        return self.value

    def to_bytes(self):
        return self.value.encode('utf-8')

    def __getattr__(self, item):
        for a in self._adapters:
            res = a(item)
            if res is not None:
                return res

    @classmethod
    def register_adapter(cls, f: Callable[['Data'], Any]):
        cls._adapters.append(f)
