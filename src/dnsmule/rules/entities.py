from typing import Callable, Optional, Union

from ..baseclasses import KwargClass, Identifiable
from ..definitions import RRType, Record, Result

RuleFunction = Callable[[Record], Union[Result, None]]


class Rule(KwargClass, Identifiable):
    """Wrapper class for rules to support priority based comparison
    """
    f: RuleFunction
    name: str = None
    priority: int = 0

    def __init__(self, f: RuleFunction = None, **kwargs):
        super(Rule, self).__init__(**kwargs)
        if 'name' not in self._properties:
            self._properties.insert(0, 'name')
        if f is not None and not callable(f):
            raise ValueError('Rule function not callable')
        elif f is None and type(self).__call__ is not Rule.__call__:
            self.f = self.__call__
        else:
            if f is None:
                raise ValueError('Rule function was None')
            self.f = f
            self._properties.insert(1, 'f')
        if not self.name and hasattr(self.f, '__name__'):
            self.name = self.f.__name__

    def __call__(self, record: Record) -> Optional[Result]:
        if self.f == self.__call__:
            raise RecursionError('Illegal state, infinite recursion detected')
        return self.f(record)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: 'Rule'):
        return isinstance(other, Rule) and other.name == self.name or other == self.name

    def __lt__(self, other):
        """Supports comparison
        """
        return self.priority > other.priority


class RuleCreator:
    """Helper for rule registration
    """
    priority: int
    type: str
    callback: Callable[[RRType, Rule], None]

    # noinspection PyShadowingBuiltins
    def __init__(self, callback: Callable[[RRType, Rule], None], type: str = None, priority: int = None):
        super().__init__()
        self.type = type
        self.priority = priority
        self.callback = callback

    def __call__(self, f: RuleFunction):
        if self.type is None:
            raise ValueError('Rule requires a record type')
        self.callback(RRType.from_any(self.type), Rule(f=f, priority=self.priority or Rule.priority))
        return f

    def __getitem__(self, priority: int):
        if self.priority is not None:
            raise ValueError('Rule already has a priority')
        return type(self)(self.callback, priority=priority)

    def __getattr__(self, rtype: str):
        if self.type is not None:
            raise ValueError('Rule already has a type')
        return type(self)(self.callback, type=rtype)


__all__ = [
    'Rule',
    'RuleFunction',
    'RuleCreator',
]
