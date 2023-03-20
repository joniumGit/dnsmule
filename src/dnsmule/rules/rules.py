from abc import ABC
from typing import Dict, Union, List, Iterable, Tuple

from .entities import Rule, RuleCreator
from .factories import RuleFactoryMixIn
from ..definitions import Record, RRType
from ..logger import get_logger


class RulesBase(RuleFactoryMixIn, ABC):
    _rules: Dict[Union[int, RRType], List[Rule]]

    def __init__(self):
        super(RulesBase, self).__init__()
        self._rules = {}

    def process(self, record: Record) -> None:
        for rule in self._rules.get(record.type, []):
            try:
                record.result += rule(record)
            except Exception as e:
                get_logger().error(f'Rule {rule.name} raised an exception', exc_info=e)

    def append(self, record: Union[str, int, RRType], rule: Rule) -> None:
        record = RRType.from_any(record)
        if record not in self._rules:
            self._rules[record] = []
        if rule in self._rules[record]:
            raise ValueError('Rule already exists')
        self._rules[record].append(rule)
        self._rules[record].sort()

    def contains(self, record: Union[str, int, RRType], name: str) -> bool:
        record = RRType.from_any(record)
        return name in self._rules[record] if record in self._rules else False

    def size(self):
        return sum(len(c) for c in self._rules.values())

    def get(self, rtype: Union[RRType, int, str]):
        rtype = RRType.from_any(rtype)
        if rtype not in self._rules:
            self._rules[rtype] = []
        return self._rules[rtype]

    def iterate(self) -> Iterable[Tuple[Union[int, RRType], List[Rule]]]:
        yield from self._rules.items()

    @property
    def types(self) -> Iterable[RRType]:
        return iter(self._rules.keys())

    @property
    def add(self) -> RuleCreator:
        return RuleCreator(callback=self.append)


class Rules(RulesBase):

    def __getitem__(self, key: Union[str, int, RRType]) -> List[Rule]:
        return self.get(key)

    def __len__(self) -> int:
        return sum(map(len, self._rules.values()))

    def __iter__(self) -> Iterable[Tuple[Union[int, RRType], List[Rule]]]:
        yield from self.iterate()

    def keys(self):
        yield from self._rules.keys()


__all__ = [
    'Rules',
    'Rule',
]
