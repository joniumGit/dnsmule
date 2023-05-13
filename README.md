# DNSMule

[![codecov](https://codecov.io/gh/joniumGit/dnsmule/branch/master/graph/badge.svg?token=54DPREJIFU)](https://codecov.io/gh/joniumGit/dnsmule)

Package for rule based dependency scanning and service fingerprinting via DNS.

This package provides utilities for writing and evaluating verbose and easy to read rule definitions in _YAML_-format.
There are two builtin rule formats with more available as plugins.

## Installation

```shell
pip install dnsmule[full] dnsmule_plugins[full]
```

This will install everything available for DNSMule. You can also choose to install components as necessary.

For installing from the repo you can use:

```shell
pip install -e .
```

## Overview

The DNSMule tool is composed in the following way:

- DNSMule
    - Backend
    - Rules
        - Rule
    - Plugins

## Examples

Check out the examples in the [examples](examples) folder. They should get you up and running quickly.

## YAML Configuration

### Summary

The tool configuration is done through one or multiple rule configuration files. The file structure is defined in the
[schema file](rules/rules-schema.yml). In addition to some builtin rule types, it is possible to create new types by
registering handlers or rules programmatically.

Rules support registration per DNS record type and priority for controlling invocation order.

```yaml
version: '0.0.1'
rules:
  - name: o365
    priority: 10
    type: dns.regex
    record: txt
    config:
      pattern: '^MS=ms'
      identification: MICROSOFT::O365
  - name: ses
    type: dns.regex
    record: txt
    config:
      pattern: '^amazonses:'
      identification: AMAZON::SES
```

#### Example

```python
from dnsmule.definitions import Record, Result
from dnsmule.rules import Rules, Rule

rules: Rules

...


@rules.add.A[10]
def my_scan(record: Record) -> Result:
    from dnsmule.logger import get_logger
    get_logger().info('Address %s', record)
    return record.tag('MY::SCAN')


@rules.register('my.rule')
def create_my_rule(**arguments) -> Rule:
    ...
```

Here the `add` is used to directly register a new rule into the ruleset with a given priority. The `register` call
creates a new handler for rules of type `my.rule`. Any future `my.rule` creations from YAML or code would be routed to
this factory function.

See the examples folder for more examples and how to use rules in code.

### Plugins and Backends

#### Plugins

It is possible to register plugins using the YAML file:

```yaml
plugins:
  - name: dnsmule_plugins.CertCheckPlugin
    config:
      callback: false
```

These are required to extend the `dnsmule.plugins.Plugin` class.
Plugins are evaluated and initialized before rules.
Any rules requiring a plugin should list their plugin in this block.
Plugins are only initialized once and if a plugin already exists in the receiving DNSMule instance
it will be ignored.

#### Backends

It is possible to define a single backend in a YAML file:

```yaml
backend:
  name: 'dnspython.DNSPythonBackend'
  config:
    timeout: 5.5
    resolver: 8.8.8.8
```

The backend must extend the `dnsmule.backends.Backend` class.
This declaration is ignored if this is not used in `DNSMule.load` or `DNSMule(file=file)`.

## Editor Support

#### Type Hints and JSON Schema (IntelliJ IDEA, PyCharm, etc.)

It is possible to register the schema file as a custom JSON schema in IntelliJ editors.
This will give access to typehints and schema validation inside rule files and is especially nice for dynamic rule
definitions as you get full editor features for python inside the snippets.

- settings...
- Languages & Frameworks > Schemas and DTDs > JSON Schema Mappings
- Add a new mapping with the schema file and specified file or pattern

This is configured in the schema using the custom intellij language injection tag:

```yml
x-intellij-language-injection:
  language: Python
  prefix: |+0
    code hints go here
    check the schema for more info
  suffix: ''
```

Currently, this supports `dns.regex` pattern regex language injection and `dns.dynamic` rule code language injection.
Type hints and quick documentation are available.

## Builtin Rules

#### Regex rules

Regex rules can be defined with either one `pattern` or multiple `patterns`.
An example is in the following snippet:

```yml
rules:
  - name: test
    type: dns.regex
    record: txt
    config:
      pattern: '^.*\.hello_world\.'
      identification: HELLO::WORLD
      flags:
        - UNICODE
        - DOTALL
  - name: generic_verification
    type: dns.regex
    record: txt
    priority: 10
    description: Generic Site Regex Collection
    config:
      patterns:
        - '^(.+)(?:-(?:site|domain))?-verification='
        - '^(.+)(?:site|domain)verification'
        - '^(.+)_verify_'
        - '^(\w+)-code:'
      group: 1
```

The full definition and additional info is available from the schema file, examples, and code.

#### Dynamic Rules

Dynamic rules are defined as code snippets with one or two methods

An init method that is invoked once after creation

```python
def init() -> None:
    add_rule(...)
```

A process function that is invoked once for each record

```python
def process(record: Record) -> Result:
    add_rule(...)
    return record.result()
```

Both of these functions have access to the following rule creation method:

```python
def add_rule(
        record_type: Union[str, int, RRType],
        rule_type: str,
        name: str,
        *,
        priority: int = 0,
        **options,
) -> None:
    """
    :param record_type: Valid DNS record type as text, int, or type
    :param rule_type:   Valid rule type factory e.g. dns.regex
    :param name:        Name of the created rule
    :param priority:    Priority for the created rule, default 0
    :param options:     Any additional options for the rule factory
    """
```

The only globals passed to these methods are:

- \_\_builtins\_\_
- RRType, Record, Result, Domain, Tag, Config
    - The Config contains the `config` property passed to the rule from YAML
- add_rule
- Any additional globals created by the code itself

When the code is exec'd the result is inspected for:

- init function without parameters
- process function with a single parameter

Some notes:

- The init function is invoked exactly once.
- The process function is invoked exactly once for every single Record.
- Any rules created from the init method will be invoked for every suitable record.
- Any rules created from the process method will be invoked for suitable records found after creation.
- Creating DynamicRules from init or process is considered undefined behaviour and care should be taken
    - The user should call init manually and include fail-safes for only calling it once
    - The add_rule callback might not be available so you need to pass it manually to the rule

## Other

### Example server

The repo has a `Dockerfile` for easily running the tool using an example server in Docker:

```shell
$ ./build-image
$ ./run-server
```

### Notice

This package is under active development.

### Additional

- RnD Scripts under [scripts](scripts)
- Example server under [server](server)
- Examples for coding under [examples](examples)