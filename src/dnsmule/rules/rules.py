from collections import defaultdict
from typing import Dict, Union, List, Mapping

from .entities import Rule, RuleCreator
from .factories import RuleFactoryMixIn
from ..config import get_logger
from ..definitions import Record, Result, RRType


class Rules(Mapping[Union[int, RRType], List[Rule]], RuleFactoryMixIn):
    """Class for storing rules
    """
    _rules: Dict[Union[int, RRType], List[Rule]]

    def __init__(self):
        super().__init__()
        self.log = get_logger()
        self._rules = defaultdict(list)

    async def process_record(self, record: Record) -> Result:
        for r in self._rules.get(record.type, []):
            try:
                t = r(record)
                if hasattr(t, '__await__'):
                    await t
            except Exception as e:
                self.log.error(f'Rule {r.name} raised an exception', exc_info=e)
        return record.result()

    def add_rule(self, rtype: Union[RRType, int, str], rule: Rule) -> None:
        rtype = RRType.from_any(rtype)
        self._rules[rtype].append(rule)
        self._rules[rtype].sort()

    def get_types(self) -> List[RRType]:
        return [*self._rules.keys()]

    @property
    def add(self) -> RuleCreator:
        return RuleCreator(callback=self.add_rule)

    def __getitem__(self, item: Union[RRType, int, str]) -> List[Rule]:
        return self._rules[RRType.from_any(item)]

    def __iter__(self):
        yield from iter(self._rules)

    def __len__(self) -> int:
        return len(self._rules)

    def rule_count(self):
        return sum(len(c) for c in self._rules.values())


__all__ = [
    'Rules',
    'Rule',
]
