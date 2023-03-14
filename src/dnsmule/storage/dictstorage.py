from threading import Lock
from typing import Union, Iterator

from .abstract import Storage
from ..definitions import Domain, Result


class DictStorage(Storage):

    def __init__(self, **kwargs):
        super(DictStorage, self).__init__(**kwargs)
        self._dict = {}
        self._lock = Lock()

    def __setitem__(self, key: Union[str, Domain], value: Union[Result, None]) -> None:
        with self._lock:
            d = {
                **self._dict,
                str(key): value,
            }
            self._dict = d

    def __delitem__(self, key: Union[str, Domain]) -> None:
        with self._lock:
            key = str(key)
            if key in self:
                d = {**self._dict}
                del d[key]
                self._dict = d

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterator[str]:
        with self._lock:
            return iter(self._dict)

    def __contains__(self, item: Union[str, Domain]):
        return str(item) in self._dict

    def __getitem__(self, key: Union[str, Domain]) -> Union[Result, None]:
        key = str(key)
        if key in self:
            return self._dict[key]


__all__ = [
    'DictStorage',
]
