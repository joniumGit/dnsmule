from pathlib import Path
from threading import Lock
from typing import Union, Dict, Mapping, List

from .backends import Backend, load_config as load_backend
from .definitions import Domain, Result
from .rules import Rules, load_config as load_rules


class DNSMule(Mapping[Union[str, Domain], Result]):
    rules: Rules
    _backend: Backend
    _data: Dict[Union[str, Domain], Result]

    @staticmethod
    def load(file: Union[str, Path]):
        return DNSMule(file=file)

    @staticmethod
    def make(rules: Rules, backend: Backend):
        return DNSMule(rules=rules, backend=backend)

    def __init__(self, file: Union[str, Path] = None, rules: Rules = None, backend: Backend = None):
        if file:
            self.rules = load_rules(file)
            self._backend = load_backend(file)
        else:
            self.rules = rules
            self._backend = backend
        if self.rules is None or self._backend is None:
            raise ValueError('Invalid Configuration')
        self.backend = type(self._backend).__name__
        self._data = dict()
        self._lock = Lock()

    def get_backend(self):
        return self._backend

    async def swap_backend(self, backend: Backend):
        await self._backend.stop()
        self._backend = backend
        await backend.start()

    def append_rules(self, f: Union[str, Path]):
        load_rules(f, rules=self.rules)

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
        async for result in self._backend.run(self.rules, *domains):
            self.store_result(result)

    def domains(self) -> List[str]:
        return [*self]

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *_):
        await self.stop()

    async def start(self):
        await self._backend.start()

    async def stop(self):
        await self._backend.stop()


__all__ = [
    'DNSMule'
]
