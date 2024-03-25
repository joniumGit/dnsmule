import re
from datetime import datetime
from types import SimpleNamespace
from typing import TypedDict, List, Union

from .api import Record, Result, RRType, Domain


def _add_to_set(key: str, result: Result, value: str):
    if key in result.data:
        result.data[key] = {*result.data[key], value}
    else:
        result.data[key] = {value}


def _add_to_list(key: str, result: Result, value: str):
    if key in result.data:
        result.data[key] = [*result.data[key], value]
    else:
        result.data[key] = [value]


class MismatchRule:
    type = 'dns.mismatch'

    def __call__(self, record: Record, result: Result):
        if record.name != result.name:
            result.tags.add('DNS::MISMATCH')
            _add_to_set('aliases', result, record.name)


class RegexRule:
    type = 'dns.regex'

    class Pattern(TypedDict):
        label: str
        group: Union[str, int]
        regex: str

    def __init__(
            self,
            *,
            name: str,
            patterns: List[Pattern],
    ):
        self.name = name.upper()
        self.patterns = [{**p, 'regex': re.compile(p['regex'])} for p in patterns]

    def __call__(self, record: Record, result: Result):
        for pattern in self.patterns:
            if m := pattern['regex'].fullmatch(record.text):
                if label := pattern.get('label', None):
                    tag = f'DNS::REGEX::{self.name}::{label}'
                else:
                    tag = f'DNS::REGEX::{self.name}::{m.group(pattern["group"])}'
                result.tags.add(tag)


class TimestampRule:
    type = 'dns.timestamp'

    def __enter__(self):
        self._stamp = datetime.now().isoformat()
        self._seen = {*()}
        return self

    def __exit__(self):
        del self._seen
        del self._stamp

    def _stamp_seen(self, result: Result):
        domain = result.name
        if domain not in self._seen:
            self._seen.add(domain)
            _add_to_list('seen', result, self._stamp)

    def _stamp_scanned(self, result: Result):
        domain = result.name
        if domain not in self._seen:
            self._seen.add(domain)
            _add_to_list('seen', result, self._stamp)
            _add_to_list('scans', result, self._stamp)
            result.data['last_scan'] = self._stamp

    def __call__(self, record: Record, result: Result):
        self._stamp_scanned(result)
        self._stamp_seen(record.result)


class ContainsRule:
    type = 'dns.contains'

    class Identity(TypedDict):
        name: str
        type: str
        value: str

    def __init__(
            self,
            *,
            identities: List[Identity],
    ):
        self.identities = identities

    def __call__(self, record: Record, result: Result):
        for o in self.identities:
            key = o['value']
            if key in record.text:
                result.tags.add('DNS::CIDER::%s::%s' % (
                    o['type'].upper(),
                    o['name'].upper(),
                ))


class DynamicRule:
    type = 'dns.dynamic'

    def __init__(
            self,
            code: str,
            name: str = 'rule',
            **config
    ):
        super().__init__()
        self.name = name.lower()
        self.code = compile(code, f'{name}.dynamic.py', 'exec')
        self.config = {**config, 'name': name}

    def __enter__(self):
        _globals = {
            '__builtins__': __builtins__,
            'RRType': RRType,
            'Record': Record,
            'Result': Result,
            'Domain': Domain,
            'Config': SimpleNamespace(**self.config)
        }
        exec(self.code, _globals)
        if 'init' in _globals:
            eval('init()', _globals)
        self._globals = _globals
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._globals

    def __call__(self, record: Record) -> Result:
        if 'process' in self._globals:
            return eval('process(record)', self._globals, {'record': record})


__all__ = [
    'MismatchRule',
    'RegexRule',
    'TimestampRule',
    'ContainsRule',
    'DynamicRule',
]
