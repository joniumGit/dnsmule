from dataclasses import dataclass
from typing import Any, Union, Dict

from .domain import Domain
from .result import Result
from .rrtype import RRType
from .tag import Tag


@dataclass(init=False, eq=True)
class Record:
    domain: Domain
    type: RRType
    data: Any

    context: Dict[str, Any]
    """Provides a place to attach arbitrary metadata to the Record
    """

    _result: Result

    # noinspection PyShadowingBuiltins
    def __init__(self, domain: Domain, type: RRType, data: Any):
        self.domain = domain
        self.type = type
        self.data = data
        self._result = Result(self.domain, initial_type=self.type)
        self.context = {}

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value: Result):
        self._result += value

    @property
    def text(self) -> str:
        return str(self.data)

    def tag(self, tag: Union[Tag, str]) -> None:
        self.result.tag(tag)

    def __hash__(self):
        return hash((self.domain, self.type))


__all__ = [
    'Record',
]
