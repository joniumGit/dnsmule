from pathlib import Path
from typing import Union, Collection, Optional, Iterable

from .backends import Backend
from .backends.noop import NOOPBackend
from .definitions import Domain, Result, RRType
from .loader import ConfigLoader
from .plugins import Plugins
from .rules import Rules
from .storages import Storage, Query
from .storages.dictstorage import DictStorage


class DNSMule:
    rules: Rules
    backend: Backend
    storage: Storage
    plugins: Plugins

    @staticmethod
    def make(
            rules: Rules = None,
            backend: Backend = None,
            storage: Storage = None,
            plugins: Plugins = None,
    ):
        if backend is None:
            backend = NOOPBackend()
        if storage is None:
            storage = DictStorage()
        if rules is None:
            rules = Rules()
        if plugins is None:
            plugins = Plugins()
        return DNSMule(
            rules=rules,
            backend=backend,
            storage=storage,
            plugins=plugins,
        )

    @staticmethod
    def load(file: Union[str, Path]):
        loader = ConfigLoader(DNSMule.make())
        loader.load_config(file)
        loader.all()
        return loader.mule

    def __init__(
            self,
            rules: Rules,
            backend: Backend,
            storage: Storage,
            plugins: Plugins,
    ):

        self.rules = rules
        self.backend = backend
        self.storage = storage
        self.plugins = plugins
        missing = [*filter(
            lambda o: getattr(self, o, None) is None,
            ['rules', 'backend', 'storage', 'plugins'],
        )]
        if missing:
            raise ValueError('Missing required attributes (%s)' % ','.join(missing))

    def append(self, config: Union[str, Path]) -> 'DNSMule':
        """
        Loads rules and plugins from a yaml configuration and adds them to this mule

        :raises ValueError: On duplicate rules
        """
        loader = ConfigLoader(self)
        loader.load_config(config)
        loader.append_plugins()
        loader.append_rules()
        return self

    def scan(self, *domains: Union[Iterable[Union[str, Domain]], Union[str, Domain]]) -> None:
        """
        Scans a domain with included rules and stores te result

        Can be called with either a single argument that is an iterable of domains
        or multiple single domains.
        """
        if all(map(lambda o: isinstance(o, str), domains)):
            domains = [*domains]
        else:
            domains = [*domains[0]]
        for domain in domains:
            if domain not in self.storage:
                self.storage.store(Result(domain))
        for record in self.backend.run(domains, *self.rules.types):
            with self.storage.using(record.result):
                self.rules.process(record)

    def result(self, domain: Union[str, Domain]) -> Optional[Result]:
        """Return a result for a domain if one exists
        """
        return self.storage.fetch(Domain(domain))

    def search(
            self,
            domains: Collection[Union[str, Domain]] = None,
            types: Collection[Union[str, int, RRType]] = None,
            tags: Collection[str] = None,
            data: Collection[str] = None,
    ):
        """Search for a result given the parameters
        """
        return self.storage.query(Query(
            domains=domains,
            types=types,
            tags=tags,
            data=data,
        ))


__all__ = [
    'DNSMule',
]
