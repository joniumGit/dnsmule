from importlib import import_module
from pathlib import Path
from typing import cast, Union, IO

from . import backends
from . import rules
from . import storages
from .api import Backend, Storage, Rules, DNSMule, Rule, BatchRule
from .rrtype import RRType


def load_by_type(*sources: object, type: str) -> type:
    for source in sources:
        for value in dir(source):
            if not value.startswith('_'):
                candidate = getattr(source, value)
                if getattr(candidate, 'type', None) == type:
                    return candidate
                if getattr(candidate, '__name__', None) == type:
                    return candidate
    raise ValueError(f"id {type} not found")


def instantiate_from_config(*sources: object, config: dict) -> object:
    type = load_by_type(*sources, type=config['type'])
    return type(**config.get('config', {}))


def instantiate_rules_from_config(*sources: object, config: list) -> Rules:
    ruleset = Rules()
    for item in config:
        record = item['record']
        rule = cast(
            Union[Rule, BatchRule],
            instantiate_from_config(
                *sources,
                config=item,
            ),
        )
        if record == 'any':
            ruleset.register_any(rule)
        elif record == 'batch':
            ruleset.register_batch(rule)
        else:
            ruleset.register(RRType.from_any(record), rule)
    return ruleset


def load_plugins(config: list):
    return [
        import_module(plugin, package='dnsmule')
        for plugin in config
    ]


def load_config(config: dict) -> DNSMule:
    plugins = load_plugins(config.get('plugins', []))
    return DNSMule(
        storage=cast(
            Storage,
            instantiate_from_config(
                storages,
                *plugins,
                config=config['storage'],
            )
        ),
        backend=cast(
            Backend,
            instantiate_from_config(
                backends,
                *plugins,
                config=config['backend'],
            )
        ),
        rules=instantiate_rules_from_config(
            rules,
            *plugins,
            config=config['rules'],
        ),
    )


def load_config_from_stream(stream: IO) -> DNSMule:
    from yaml import safe_load
    return load_config(safe_load(stream))


def load_config_from_file(file: Union[str, Path]) -> DNSMule:
    with open(file, 'r') as f:
        return load_config_from_stream(f)


__all__ = [
    'load_config_from_file',
    'load_config_from_stream',
    'load_config',
]
