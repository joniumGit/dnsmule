from abc import ABC, abstractmethod
from threading import RLock
from typing import TYPE_CHECKING, Type, Union, Dict, Any, Optional

from ..utils import KwargClass, Identifiable

if TYPE_CHECKING:  # pragma: nocover
    from ..mule import DNSMule


class Plugin(KwargClass, Identifiable, ABC):

    @abstractmethod
    def register(self, mule: 'DNSMule'):
        """NOOP
        """


class Plugins:
    _dict: Dict[str, Plugin]

    def __init__(self):
        self._dict = {}
        self._lock = RLock()

    def add(self, plugin: Plugin):
        with self._lock:
            self._dict[plugin.id] = plugin

    def get(self, plugin: Union[Type[Plugin], str]) -> Optional[Plugin]:
        if isinstance(plugin, type) and issubclass(plugin, Plugin):
            return self._dict.get(plugin.id, None)
        else:
            return self._dict.get(plugin, None)

    def contains(self, item: Any):
        return self.get(item) is not None

    def __contains__(self, item):
        return self.contains(item)

    def __getitem__(self, item):
        return self.get(item)

    def __iter__(self):
        yield from self._dict.keys()


__all__ = [
    'Plugin',
    'Plugins',
]
