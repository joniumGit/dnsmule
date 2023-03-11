from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: nocover
    from ..mule import DNSMule


class Plugin(ABC):

    def __init__(self, **kwargs):
        self.__dict__.update({
            k: v
            for k, v in kwargs.items()
            if not k.startswith('_')
        })

    @abstractmethod
    def register(self, mule: 'DNSMule'):
        """NOOP
        """


__all__ = [
    'Plugin',
]
