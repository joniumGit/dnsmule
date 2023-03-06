from typing import Callable, Collection

from dnsmule.rules import Rules
from .rule import CertChecker


def plugin_certcheck(rules: Rules, datasource_callback: Callable[[Collection[str]], None]):
    rules.register('ip.certs')(CertChecker.creator(datasource_callback))


__all__ = [
    'plugin_certcheck',
]
