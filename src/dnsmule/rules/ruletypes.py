import functools
import operator
import re
from typing import Any
from typing import List
from typing import Union

from .entities import Rule, RuleFactory
from ..definitions import Result, Record, RRType


class RegexRule(Rule):
    pattern: str
    patterns: List[str]

    identification: str = None
    flags: List[str] = None
    attribute: str = 'to_text'
    group: Union[int, str] = None

    _patterns: List[re.Pattern]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_patterns()

    def create_patterns(self):
        all_flags = {k.lower(): v for k, v in re.RegexFlag.__members__.items()}

        if self.flags:
            flags = [all_flags[str(flag)] for flag in map(str.lower, self.flags) if flag in all_flags]
            if len(flags) != len(self.flags):
                raise ValueError('Invalid Regex Flags')
            flags = functools.reduce(operator.or_, flags)
        else:
            flags = re.UNICODE

        self._patterns = []
        if getattr(self, 'pattern', False):
            self._patterns.append(re.compile(self.pattern, flags=flags))
        if getattr(self, 'patterns', False):
            self._patterns.extend(re.compile(p, flags=flags) for p in self.patterns)

    def get_attribute(self, record: Record):
        """Resolves attribute from record

        Also strips any leading or trailing quotes
        """
        attr = getattr(record.data, self.attribute)
        if callable(attr):
            out = str(attr())
        else:
            out = str(attr)
        return out

    def __call__(self, record: Record):
        """Calls through all patterns and finds first identification
        """
        for p in self._patterns:
            m = p.search(self.get_attribute(record))
            if m:
                _id = self.identification if self.group is None else m.group(self.group)
                if _id:
                    _id = _id.upper()
                else:
                    _id = 'UNKNOWN'
                return record.identify(f'DNS::REGEX::{self.name.upper()}::{_id}')


class DynamicRule(Rule):
    code: str
    globals: dict

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.globals = {
            '__builtins__': __builtins__,
            'RRType': RRType,
            'Record': Record,
            'Result': Result,
        }
        if not self.code:
            raise ValueError('No code provided')
        self._code = compile(self.code, 'dynamic_rule.py', 'exec')

    def init(self, create_callback: RuleFactory):
        def add_rule(record_type: Any, rule_type: str, name: str, priority: int = 0, **options):
            create_callback(name, {
                'record': record_type,
                'type': rule_type,
                'priority': priority,
                **options,
            })

        self.globals['add_rule'] = add_rule
        exec(self._code, self.globals)
        if 'init' in self.globals:
            eval('init()', self.globals)

    def __call__(self, record: Record) -> Result:
        if 'process' in self.globals:
            return eval('process(record)', self.globals, {'record': record})


__all__ = [
    'DynamicRule',
    'RegexRule',
]
