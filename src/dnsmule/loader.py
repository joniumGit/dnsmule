from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Dict, List, Any, Type, TypeVar, Union, Optional, cast, Callable, Generic

from .backends import Backend
from .backends.noop import NOOPBackend
from .config import get_logger
from .definitions import RRType
from .plugins import Plugin
from .rules import Rules, DynamicRule
from .rules.entities import RuleFactory

T = TypeVar('T')


@dataclass
class Initializer(Generic[T]):
    type: str
    f: Callable[[...], T]

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)


@dataclass
class Config:
    rules: Optional[Initializer[Rules]]
    backend: Optional[Initializer[Backend]]
    plugins: Optional[List[Initializer[Plugin]]]


def load_and_append_rule(
        rules: Rules,
        record: RRType,
        rule_type: str,
        config: Dict[str, Any],
) -> None:
    """Creates a rule from rule definition

    Initializes any dynamic rules created and passes the add_rule callback to them
    """
    rule = rules.create_rule(rule_type, config)
    if isinstance(rule, DynamicRule):
        rule.init(cast(RuleFactory, partial(load_and_append_rule, rules)))
    rules.add_rule(record, rule)


def load_rules(config: List[Dict[str, Any]], rules: Rules = None) -> Rules:
    """Loads rules from the rules element in rules.yml

    Provider rules in case of non-default handlers.
    """
    rules = Rules() if rules is None else rules
    for rule_definition in config:
        record = RRType.from_any(rule_definition['record'])
        config = rule_definition.get('config', {})
        rtype = rule_definition['type']
        name = rule_definition['name']
        if 'name' not in config:
            config['name'] = name
        if not rules.has_rule(record, name):
            try:
                load_and_append_rule(rules, record, rtype, config)
            except KeyError as e:
                get_logger().error(f'Failed to load rule: {rtype} RuleTypeNotFound({e})')
        else:
            raise ValueError(f'Can not add duplicate rule: {name} ({rtype})')
    return rules


def import_class(import_string: str, parent: Type[T], relative: bool = True, package: str = None) -> Type[T]:
    """Imports a module and gets the last part as attribute from it

    **Note:** This allows arbitrary imports and code execution
    """
    module, _, cls = import_string.rpartition('.')

    import importlib

    if relative:
        m = importlib.import_module(f'.{module}', package=package)
    else:
        m = importlib.import_module(module, package=package)

    cls = getattr(m, cls)
    if not issubclass(cls, parent):
        raise ImportError(f'Tried loading an incompatible class from {import_string} ({parent.__name__})')
    else:
        return cls


def make_backend(document: Dict[str, Any]) -> Initializer[Backend]:
    """Loads backend from yaml config
    """
    backend: Dict[str, Any] = document.get('backend', None)
    if backend:
        backend_type = backend['name']
        backend_config = backend.get('config', {})
        try:
            backend_class = import_class(backend_type, Backend, relative=True, package='dnsmule.backends')
        except ImportError as e:
            try:
                backend_class = import_class(backend_type, Backend, relative=False)
            except ImportError as ex:
                raise ex from e
            except AttributeError as ex:
                raise ImportError from ex
        except AttributeError as e:
            raise ImportError from e

        return Initializer(type=backend_type, f=partial(backend_class, **backend_config))
    else:
        return Initializer(type=NOOPBackend.__name__, f=NOOPBackend)


def make_rules(document: Dict[str, Any]) -> Initializer[Rules]:
    """Loads rules from yaml config
    """
    config: List[Dict[str, Any]] = document.get('rules', [])
    return Initializer(type='Rules', f=partial(load_rules, config))


def make_plugins(document: Dict[str, Any]) -> List[Initializer[Plugin]]:
    """Loads plugins from yaml config
    """
    plugins: List[Dict[str, Any]] = document.get('plugins', [])
    out: List[Initializer[Plugin]] = []
    for plugin in plugins:
        plugin_type = plugin['name']
        plugin_config = plugin.get('config', {})
        try:
            plugin_class = import_class(plugin_type, Plugin, relative=False)
            out.append(Initializer(type=plugin_type, f=partial(plugin_class, **plugin_config)))
        except ImportError as e:
            get_logger().error(f'Failed to load plugin: {plugin_type} PluginNotFound({e})')
    return out


def load_config(
        file: Union[str, Path],
        rules: bool = True,
        backend: bool = True,
        plugins: bool = True,
) -> Config:
    """Loads a yaml config
    """
    import yaml
    with open(file, 'r') as f:
        document = yaml.safe_load(f)
        return Config(
            plugins=make_plugins(document) if plugins else None,
            backend=make_backend(document) if backend else None,
            rules=make_rules(document) if rules else None,
        )


__all__ = [
    'load_config',
    'Config',
    'load_and_append_rule',
]
