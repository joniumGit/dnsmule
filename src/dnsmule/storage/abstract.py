from abc import ABC, abstractmethod
from typing import Iterator, Union

from ..definitions import Domain, Result


class Storage(ABC):

    def __init__(self, **kwargs):
        self.__dict__.update({
            k: v
            for k, v in kwargs.items()
            if not k.startswith('_')
        })

    @abstractmethod
    def __setitem__(self, key: Union[str, Domain], value: Union[Result, None]) -> None:
        """Save a result or none
        """

    @abstractmethod
    def __delitem__(self, key: Union[str, Domain]) -> None:
        """Delete a result if one exists
        """

    @abstractmethod
    def __getitem__(self, key: Union[str, Domain]) -> Union[Result, None]:
        """Get a result if one exists
        """

    @abstractmethod
    def __len__(self) -> int:
        """Return the current size
        """

    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        """Iterate all keys
        """

    @abstractmethod
    def __contains__(self, item: Union[str, Domain]):
        """Check if the result is found
        """


__all__ = [
    'Storage',
]
