from collections import defaultdict
from typing import Dict, Union, List, Set

from .entities import Rule, Record, Result, RuleCreator, Type
from .factories import RuleFactoryMixIn
from ..config import get_logger


class Rules(RuleFactoryMixIn):
    """Class for storing rules
    """
    _rules: Dict[Type, List[Rule]]

    def __init__(self):
        super().__init__()
        self.log = get_logger()
        self._rules = defaultdict(list)

    def process_record(self, record: Record) -> Result:
        for r in self._rules.get(record.type, []):
            try:
                r(record)
            except Exception as e:
                self.log.error(f'Rule {r.name} raised an exception', exc_info=e)
        return record.result()

    def add_rule(self, rtype: Union[Type, int, str], rule: Rule) -> None:
        rtype = Type.from_any(rtype)
        self._rules[rtype].append(rule)
        self._rules[rtype].sort()

    def get_rtypes(self) -> List[Type]:
        return [*self._rules.keys()]

    @property
    def add(self) -> RuleCreator:
        return RuleCreator(callback=self.add_rule)

    def __getitem__(self, item: Union[Type, int, str]) -> List[Rule]:
        return self._rules[Type.from_any(item)]


__all__ = [
    'Rules',
]
