from abc import abstractmethod
from types import MethodType
from typing import Iterable, Optional

from . import Result, Domain
from .baseclasses import Identifiable
from .storages import Query
from .storages.abstract import Storage


class Adapter(Identifiable):
    """Adds capability to patch results coming and going from storage
    """

    def __init__(self, loader, saver):
        """
        :param loader: Function to call when loading a result, returns a result with modifications applied
        :param saver: Function to call when saving a result, returns a result with modifications applied
        """
        self.loader = loader
        self.saver = saver

    @abstractmethod
    def from_storage(self, result: Result) -> Result:
        """Convert entries in data from a storage form to something user defined
        """
        return self.loader(result)

    @abstractmethod
    def to_storage(self, result: Result) -> Result:
        """Convert to form suitable for going into the storage
        """
        return self.saver(result)


def patch_method(instance: Storage, method: str):
    """
    Decorator to patch an instance method

    **Note:** The usual *self* is actually the old method instance
    """
    old_method = getattr(instance, method)

    def patcher(target):
        setattr(instance, method, MethodType(target, old_method))
        return target

    return patcher


def patch_storage(delegate: Storage, adapter: Adapter) -> None:
    """
    Patches a storage with the given adapter

    This can be used to add transformations to data in result so that it is easier to handle in code.
    A usual use-case would be to deserialize some json values from the result data.
    """

    @patch_method(delegate, 'store')
    def _(method, result: Result) -> None:
        return method(adapter.to_storage(result))

    @patch_method(delegate, 'fetch')
    def _(method, domain: Domain) -> Optional[Result]:
        result = method(domain)
        if result is not None:
            return adapter.from_storage(result)

    @patch_method(delegate, 'results')
    def _(method) -> Iterable[Result]:
        yield from map(adapter.from_storage, method())

    @patch_method(delegate, 'query')
    def _(method, query: Query) -> Iterable[Result]:
        yield from map(adapter.from_storage, method(query))


__all__ = [
    'Adapter',
    'patch_storage',
]
