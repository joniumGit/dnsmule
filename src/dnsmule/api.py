from contextlib import ExitStack
from typing import (
    Iterable,
    Optional,
    Dict,
    List,
    Set,
    Any,
    Mapping,
    Union,
    Protocol,
    NewType,
    cast,
)

from .rrtype import RRType

Domain = NewType('Domain', str)


class Result:
    name: Domain
    types: Set[RRType]
    tags: Set[str]
    data: Dict[str, Any]

    def __init__(
            self,
            name: Domain,
            types: Iterable[RRType] = None,
            tags: Iterable[str] = None,
            data: Mapping[str, Any] = None,
    ):
        self.name = name
        self.types = {*types} if types is not None else {*()}
        self.tags = {*tags} if tags is not None else {*()}
        self.data = {**data} if data is not None else {}

    def __eq__(self, other: Any) -> bool:
        return other is self or (
                other.name == self.name
                and other.types == self.types
                and other.tags == self.tags
                and other.data == self.data
        )

    def __hash__(self) -> int:
        return self.data.__hash__()


class Record:
    name: Domain
    type: RRType
    data: Union[bytes, str, Any]

    def __init__(
            self,
            name: Domain,
            type: RRType,
            data: Any,
    ):
        self.name = name
        self.type = type
        self.data = data

    @property
    def text(self) -> str:
        if hasattr(self.data, 'decode'):
            return self.data.decode()
        else:
            return f'{self.data}'

    def __eq__(self, other: Any) -> bool:
        return other is self or (
                other.name == self.name
                and other.type == self.type
                and other.data == self.data
        )

    def __hash__(self) -> int:
        return (
            self.name,
            self.type,
        ).__hash__()


class Storage:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """No-op
        """

    def fetch(self, domain: Domain) -> Optional[Result]:
        """
        Fetches a record from backing storage if one exists

        :param domain: Domain to fetch the result ofr
        :return:       Result or None
        """

    def store(self, result: Result) -> None:
        """
        Stores a result into backing storage

        :param result: Result instance
        :return:       No return
        """


class Backend:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """No-op
        """

    def scan(self, domain: Domain, *records: RRType) -> Iterable[Record]:
        """
        Scans a domain for the given record types

        :param domain:  Valid domain name
        :param records: DNS record types
        :return:        Iterable of found records
        """


class _Init(Protocol):

    def __enter__(self):
        """Resource allocation
        """

    def __exit__(self, exc_type, exc_val, exc_tb):
        """No-op
        """


class PlainRule(Protocol):

    def __call__(self, record: Record, result: Result):
        """Signature
        """


class ContextRule(PlainRule, _Init):
    """Rule that has initialization
    """


Rule = Union[PlainRule, ContextRule]
"""
Rule function processes the given record.
The result of the current scan is given as the second parameter.

**NOTE**: records own result might be different from the scan result!
"""


class PlainBatchRule(Protocol):

    def __call__(self, records: List[Record], result: Result):
        """Signature
        """


class ContextBatchRule(PlainBatchRule, _Init):
    """Batch rule that has initialization
    """


BatchRule = Union[PlainBatchRule, ContextBatchRule]
"""
Batch rule function processes all records from a scan.
The result of the current scan is given as the second parameter.

**NOTE**: records own result might be different from the scan result!
"""


class Rules:
    normal: Dict[int, List[Rule]]
    after: List[BatchRule]

    def __init__(self):
        self.normal = {}
        self.after = []

    def _gen_all_rules(self):
        for group in self.normal.values():
            yield from group
        for rule in self.after:
            yield rule

    def __enter__(self):
        self._stack = ExitStack()
        self._stack.__enter__()
        for rule in self._gen_all_rules():
            if hasattr(rule, '__enter__'):
                self._stack.enter_context(rule)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._stack.__exit__(exc_type, exc_val, exc_tb)

    @property
    def records(self):
        records = {*self.normal.keys()}
        # TODO: Document and test
        if RRType.ANY in records:
            records.remove(RRType.ANY)
        return records

    def register(self, record: int, rule: Rule = None):
        if rule is None:
            def decorator(value):
                return self.register(record, value)

            return decorator
        else:
            if record not in self.normal:
                self.normal[record] = []
            self.normal[record].append(rule)
            return rule

    def register_batch(self, rule: BatchRule):
        if rule is None:
            def decorator(value):
                return self.register_batch(value)

            return decorator
        else:
            self.after.append(rule)
            return rule


class DNSMule:
    storage: Storage
    backend: Backend
    rules: Rules

    def __init__(
            self,
            storage: Storage,
            backend: Backend,
            rules: Rules,
    ):
        self.storage = storage
        self.backend = backend
        self.rules = rules

    def __enter__(self):
        self._stack = ExitStack()
        self._stack.__enter__()
        self._stack.enter_context(self.storage)
        self._stack.enter_context(self.backend)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._stack.__exit__(exc_type, exc_val, exc_tb)

    def _run_rules(self, record: Record, result: Result):
        ruleset = self.rules.normal
        if record.type in ruleset:
            for rule in ruleset[record.type]:
                rule(record, result)
        if RRType.ANY in ruleset:
            for rule in ruleset[RRType.ANY]:
                rule(record, result)

    def _run_batch_rules(self, records: List[Record], result: Result):
        if records:
            for rule in self.rules.after:
                rule(records, result)

    def _scan(self, domain: Domain, result: Result):
        for record in self.backend.scan(domain, *self.rules.records):
            result.types.add(record.type)
            yield record

    def _normal_scan(self, domain: Domain, result: Result):
        for record in self._scan(domain, result):
            self._run_rules(record, result)

    def _batched_scan(self, domain: Domain, result: Result):
        batch = []
        for record in self._scan(domain, result):
            self._run_rules(record, result)
            batch.append(record)
        self._run_batch_rules(batch, result)

    def scan(self, domain: str) -> Result:
        domain = cast(Domain, domain)
        with self.rules:
            result = self.storage.fetch(domain)
            if result is None:
                result = Result(name=domain)
            if self.rules.after:
                self._batched_scan(domain, result)
            else:
                self._normal_scan(domain, result)
            self.storage.store(result)
            return result
