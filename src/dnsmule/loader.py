from functools import partial
from pathlib import Path
from typing import Dict, List, Any, Type, TypeVar, Union, cast, TYPE_CHECKING

from .backends import Backend
from .definitions import RRType
from .logger import get_logger
from .plugins import Plugin
from .rules import Rules, DynamicRule
from .rules.entities import RuleFactory
from .storages import Storage
from .storages.dictstorage import DictStorage

if TYPE_CHECKING:  # pragma: nocover
    from .mule import DNSMule

T = TypeVar('T')


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


def import_full(
        name: str,
        cls: Type[T],
        package: str,
) -> Type[T]:
    """Helper for imports
    """
    try:
        result = import_class(name, cls, relative=True, package=package)
    except ImportError as e:
        try:
            result = import_class(name, cls, relative=False)
        except ImportError as ex:
            raise ex from e
        except AttributeError as ex:
            raise ImportError from ex
    except AttributeError as e:
        raise ImportError from e
    return result


def load_and_append_rule(
        rules: Rules,
        record: RRType,
        rule_type: str,
        config: Dict[str, Any],
) -> None:
    """Creates a rule from rule definition

    Initializes any dynamic rules created and passes the add_rule callback to them
    """
    rule = rules.create(rule_type, config)
    if isinstance(rule, DynamicRule):
        rule.init(cast(RuleFactory, partial(load_and_append_rule, rules)))
    rules.append(record, rule)


class ConfigLoader:
    mule: 'DNSMule'
    config: Dict[str, Union[List[Dict[str, Any]], Dict[str, Any]]]

    def __init__(self, mule: 'DNSMule'):
        self.mule = mule

    def set_storage(self):
        storage_definition: Dict[str, Any] = self.config.get('storage', {})
        if storage_definition:
            storage_type = storage_definition['name']
            try:
                storage_class = import_full(storage_type, Storage, 'dnsmule.storages')
                self.mule.storage = storage_class(**storage_definition.get('config', {}))
            except Exception as e:
                if storage_definition.get('fallback', False):
                    self.mule.storage = DictStorage()
                    get_logger().error(f'Failed to initialize storage {storage_type}', exc_info=e)
                else:
                    raise e

    def set_backend(self):
        backend_definition: Dict[str, Any] = self.config.get('backend', {})
        if backend_definition:
            backend_type = backend_definition['name']
            backend_class = import_full(backend_type, Backend, 'dnsmule.backends')
            self.mule.backend = backend_class(**backend_definition.get('config', {}))

    def append_rules(self):
        rule_definitions: List[Dict[str, Any]] = self.config.get('rules', [])
        if rule_definitions:
            for rule_definition in rule_definitions:
                record = RRType.from_any(rule_definition['record'])
                config = rule_definition.get('config', {})
                rtype = rule_definition['type']
                name = rule_definition['name']
                if 'name' not in config:
                    config['name'] = name
                if not self.mule.rules.contains(record, name):
                    try:
                        load_and_append_rule(self.mule.rules, record, rtype, config)
                    except KeyError as e:
                        get_logger().error(f'Failed to load rule type {rtype}, {name}: {repr(e)}')
                    except Exception as e:
                        get_logger().error(f'Failed to load rule {rtype}, {name}', exc_info=e)
                else:
                    raise ValueError(f'Can not add duplicate rule: {name} ({rtype})')

    def append_plugins(self):
        plugin_definitions: List[Dict[str, Any]] = self.config.get('plugins', [])
        if plugin_definitions:
            for plugin in plugin_definitions:
                plugin_type = plugin['name']
                plugin_config = plugin.get('config', {})
                try:
                    plugin_class = import_class(plugin_type, Plugin, relative=False)
                    if not self.mule.plugins.contains(plugin_class):
                        plugin = plugin_class(**plugin_config)
                        self.mule.plugins.add(plugin)
                        plugin.register(self.mule)
                except ImportError as e:
                    get_logger().error(f'Failed to load plugin: {plugin_type}', exc_info=e)

    def load_config(self, file: Union[str, Path]):
        import yaml
        with open(file, 'r') as f:
            self.config = yaml.safe_load(f)

    def all(self):
        self.append_plugins()
        self.append_rules()
        self.set_storage()
        self.set_backend()


__all__ = [
    'load_and_append_rule',
    'ConfigLoader',
]
