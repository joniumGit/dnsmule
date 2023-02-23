from typing import List, Callable, Optional, Dict

from .data import Type, Record, Result
from .types import RULE_TYPE


class DynamicRule:

    def __init__(self, name: str, code: str):
        self._globals = {
            '__builtins__': __builtins__,
            'Rule': RULE_TYPE,
            'Type': Type,
            'Record': Record,
            'Result': Result,
            'List': List,
            'Optional': Optional,
        }
        self._code = compile(code, name, 'exec')

    def init(self, create_and_register_rule_from_config: Callable[[Dict], None]):
        def add_rule(record_type: Type, rule_type: str, priority: int = 0, **options):
            create_and_register_rule_from_config({
                'record': record_type.__str__(),
                'type': rule_type,
                'priority': priority,
                **options,
            })

        self._globals['add_rule'] = add_rule
        exec(self._code, self._globals)
        eval('create()', self._globals)

    def __call__(self, record: Record) -> Result:
        return eval('prepare(record)', self._globals, {'record': record}) or record.result()


__all__ = [
    'DynamicRule',
]
