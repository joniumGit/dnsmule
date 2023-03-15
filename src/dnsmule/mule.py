from pathlib import Path
from typing import Union, Mapping, List, Set

from .backends import Backend
from .config import get_logger
from .definitions import Domain, Result
from .loader import load_config, Config
from .rules import Rules
from .storage import Storage


class DNSMule(Mapping[Union[str, Domain], Result]):
    rules: Rules
    backend: Backend
    plugins: Set[str]
    storage: Storage

    @staticmethod
    def load(file: Union[str, Path]):
        return DNSMule(file=file)

    @staticmethod
    def make(rules: Rules = None, backend: Backend = None, storage: Storage = None):
        if backend is None:
            from .backends.noop import NOOPBackend
            backend = NOOPBackend()
        if storage is None:
            from .storage.dictstorage import DictStorage
            storage = DictStorage()
        if rules is None:
            rules = Rules()
        return DNSMule(rules=rules, backend=backend, storage=storage)

    def __init__(
            self,
            file: Union[str, Path] = None,
            rules: Rules = None,
            backend: Backend = None,
            storage: Storage = None,
    ):
        self.plugins = set()
        if rules is not None:
            self.rules = rules
        if backend is not None:
            self.backend = backend
        if storage is not None:
            self.storage = storage
        if file:
            config = load_config(file)
            if backend is None:
                self.backend = config.backend()
            if storage is None:
                self.storage = config.storage()
            if rules is None:
                self.rules = Rules()
            self._append_plugins(config)
            self._append_rules(config)
        if getattr(self, 'rules', None) is None or getattr(self, 'backend', None) is None:
            raise ValueError('Both Rules and Backend Required')

    @property
    def backend_type(self):
        return type(self.backend).__name__

    async def swap_backend(self, backend: Backend):
        await self.backend.stop()
        self.backend = backend
        await backend.start()

    def _append_plugins(self, cfg: Config):
        for plugin_initializer in cfg.plugins:
            if plugin_initializer.type not in self.plugins:
                try:
                    plugin_initializer().register(self)
                except Exception as e:
                    get_logger().error(f'Failed to load plugin: {plugin_initializer.type} ({repr(e)})')
                else:
                    self.plugins.add(plugin_initializer.type)
            else:
                get_logger().debug(f'Plugin already loaded: {plugin_initializer.type}')

    def _append_rules(self, cfg: Config):
        cfg.rules(rules=self.rules)

    def append_config(self, f: Union[str, Path]):
        """Loads rules and plugins from a yaml configuration and adds them to this mule

        :raises ValueError: On duplicate rules
        """
        cfg = load_config(
            f,
            rules=True,
            backend=False,
            plugins=True,
        )
        self._append_plugins(cfg)
        self._append_rules(cfg)

    def store_result(self, result: Result):
        self.storage[result.domain] = result

    def store_domains(self, *domains: str):
        for domain in domains:
            if domain not in self.storage:
                self.storage[domain] = Result(Domain(domain))

    def __getitem__(self, domain: str):
        if domain in self:
            return self.storage[domain]

    def __contains__(self, domain: str):
        return domain in self.storage

    def __iter__(self):
        yield from sorted(iter(self.storage))

    def __len__(self) -> int:
        return len(self.storage)

    async def run(self, *domains: str):
        self.store_domains(*domains)
        async for record in self.backend.run(self.rules, *domains):
            existing = self.storage[record.domain]
            if existing:
                record.result() + existing
            result = await self.rules.process_record(record)
            self.store_result(result)

    def domains(self) -> List[str]:
        return [*self]

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.stop()

    async def start(self):
        await self.backend.start()

    async def stop(self):
        await self.backend.stop()


__all__ = [
    'DNSMule',
]
