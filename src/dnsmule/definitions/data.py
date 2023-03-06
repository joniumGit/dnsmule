from typing import Callable, Any, Dict, List

from .rrtype import RRType


class Data:
    type: RRType
    value: str
    data: Dict[str, any]
    _adapters: List[Callable[['Data', str], Any]] = []

    # noinspection PyShadowingBuiltins
    def __init__(self, type: RRType, value: str, **kwargs):
        self.type = RRType.from_any(type)
        self.value = value
        self.data = {**kwargs}
        self._adapters = []

    def to_text(self):
        return self.value

    def to_bytes(self):
        return self.value.encode('utf-8')

    def __str__(self):
        if self.data:
            args = ','
            args += ','.join(
                f'{k}={repr(k)}'
                for k in self.data
            )
        else:
            args = ''
        return f'{type(self).__name__}(type="{RRType.to_text(self.type)}",value="{self.value}"{args})'

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.type)

    def __eq__(self, other: 'Data'):
        return isinstance(other, Data) and other.type == self.type and other.value == self.value

    def __getattr__(self, item):
        for a in type(self)._adapters:
            res = a(self, item)
            if res is not None:
                return res
        raise AttributeError('Data has no attribute or adapter for attribute', item)

    @classmethod
    def register_adapter(cls, f: Callable[['Data', str], Any]):
        cls._adapters.append(f)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, item):
        return item in self.data
