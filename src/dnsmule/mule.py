from pathlib import Path
from threading import Lock
from typing import Union, Dict, Mapping, List

from .backends import Backend, load_config as load_backend, find_backend
from .definitions import Domain, Result
from .rules import Rules, load_config as load_rules


class DNSMule(Mapping[Union[str, Domain], Result]):
    rules: Rules
    _backend: Backend
    _data: Dict[Union[str, Domain], Result]

    def __init__(self, file: Union[str, Path] = None, rules: Rules = None, backend: Backend = None):
        if not rules:
            self.rules = load_rules(file)
        else:
            self.rules = rules
        if not backend:
            self._backend = load_backend(file, self.rules)
        else:
            self._backend = backend
        self.backend = type(self._backend).__name__
        self._data = dict()
        self._lock = Lock()

    def get_backend(self):
        return self._backend

    def swap_backend(self, backend: str, **config):
        self._backend = find_backend(backend)(self.rules, **config)

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
        yield from iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    async def run(self, *domains: str):
        self.store_domains(*domains)
        if len(domains) == 1:
            async for result in self._backend.run_single(Domain(domains[0])):
                self.store_result(result)
        else:
            async for result in self._backend.run(*map(Domain, domains)):
                self.store_result(result)

    def domains(self) -> List[str]:
        return [*sorted(self._data.keys())]


__all__ = [
    'DNSMule'
]
