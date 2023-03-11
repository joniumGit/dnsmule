from pathlib import Path
from threading import Lock
from typing import Union, Dict, Mapping, List, Set

from .backends import Backend
from .config import get_logger
from .definitions import Domain, Result
from .loader import load_config, Config
from .rules import Rules


class DNSMule(Mapping[Union[str, Domain], Result]):
    rules: Rules
    backend: Backend
    plugins: Set[str]

    _data: Dict[Union[str, Domain], Result]

    @staticmethod
    def load(file: Union[str, Path]):
        return DNSMule(file=file)

    @staticmethod
    def make(rules: Rules, backend: Backend):
        return DNSMule(rules=rules, backend=backend)

    def __init__(self, file: Union[str, Path] = None, rules: Rules = None, backend: Backend = None):
        self.plugins = set()
        if rules is not None:
            self.rules = rules
        if backend is not None:
            self.backend = backend
        if file:
            config = load_config(file)
            if backend is None:
                self.backend = config.backend()
            if rules is None:
                self.rules = Rules()
            self._append_plugins(config)
            self._append_rules(config)
        if getattr(self, 'rules', None) is None or getattr(self, 'backend', None) is None:
            raise ValueError('Both Rules and Backend Required')
        self._data = dict()
        self._lock = Lock()

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
                self.plugins.add(plugin_initializer.type)
                plugin_initializer().register(self)
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
        with self._lock:
            if result.domain in self._data:
                self._data[result.domain] += result
            else:
                self._data[result.domain] = result

    def store_domains(self, *domains: str):
        with self._lock:
            for domain in domains:
                if domain not in self._data:
                    self._data[domain] = Result(Domain(domain))

    def __getitem__(self, domain: str):
        if domain in self:
            return self._data[domain]

    def __contains__(self, domain: str):
        return domain in self._data

    def __iter__(self):
        yield from sorted(iter(self._data))

    def __len__(self) -> int:
        return len(self._data)

    async def run(self, *domains: str):
        self.store_domains(*domains)
        async for result in self.backend.run(self.rules, *domains):
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
