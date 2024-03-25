import re
from datetime import datetime
from types import SimpleNamespace
from typing import TypedDict, List, Union

from .api import Record, Result, RRType, Domain
from .utils import extend_set, extend_list


class MismatchRule:
    """
    Finds any mismatches between records and the queried domain

    For example when a domain with CNAME is queried for A records
    this will collect any aliases that can be detected from the record name fields
    not being equal.

    **Tags**::

        DNS::MISMATCH

    """
    type = 'dns.mismatch'

    def __call__(self, record: Record, result: Result):
        if record.name != result.name:
            result.tags.add('DNS::MISMATCH')
            extend_set(result.data, 'aliases', record.name)


class RegexRule:
    """
    Regular expression matching for records

    The configuration is provided as a list of patterns::

        {
          "name": <str, name of rule>
          "patterns:" [
               {
                 "label": <null, missing, or string>,
                 "regex": <regular expression string>
                 "group": <int or string
               }
          ]
        }

    You must provide either a label or a group for each pattern.

    **Tags**::

        UPPER(DNS::REGEX::$name::$label or group)

    """
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
        self.name = name
        self.patterns = [{**p, 'regex': re.compile(p['regex'])} for p in patterns]

    def __call__(self, record: Record, result: Result):
        for pattern in self.patterns:
            if m := pattern['regex'].search(record.text):
                if label := pattern.get('label', None):
                    tag = f'DNS::REGEX::{self.name}::{label}'
                else:
                    tag = f'DNS::REGEX::{self.name}::{m.group(pattern["group"])}'
                result.tags.add(tag.upper())


class TimestampRule:
    """
    Adds scan and last seen times to results

    Uses the following keys:

    - last_scan <timestamp>
    - scans     <array of timestamps>
    """
    type = 'dns.timestamp'

    def __enter__(self):
        self._stamp = datetime.now().isoformat()
        self._seen = {*()}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self._seen
        del self._stamp

    def __call__(self, record: Record, result: Result):
        domain = result.name
        if domain not in self._seen:
            self._seen.add(domain)
            extend_list(result.data, 'scans', self._stamp)
            result.data['last_scan'] = self._stamp


class ContainsRule:
    """
    Rule for simple contains checks

    Config is provided similarly to the RegexRule.
    Identities are given as a list in the _identities_ keyword argument.
    The format for identities is::

        {
          "patterns:" [
               {
                 "name": <name of the matched item>,
                 "type": <type of the matched item>
                 "value": <string to match to records>
               }
          ]
        }

    **Tags**::

        UPPER(DNS::CIDER::$type::$name)

    """
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
                tag = 'DNS::CIDER::%s::%s' % (o['type'], o['name'])
                result.tags.add(tag.upper())


class DynamicRule:
    """
    Dynamic rule that takes Python code as input

    Code is compiled and executed in different stages of the pipeline.
    The _init_ method is called when a scan is started or the rule context entered otherwise.
    For each record the process method is called if one exists.

    **Note**: This is a security risk if you ever let other people create dynamic rules
    """
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
