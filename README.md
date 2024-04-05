# DNSMule (WIP)

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

The DNSMule tool takes YAML config as input and uses it to scan a domain:

```shell
python -m dnsmule --config rules/rules.yml example.com
```

This wil give output similar to this:

````json
{
    "name": "example.com",
    "types": [
        "TXT",
        "A"
    ],
    "tags": [],
    "data": {
        "resolvedCertificates": [
            {
                "version": "v3",
                "common": "www.example.org",
                "alts": [
                    "www.example.org",
                    "example.net",
                    "example.edu",
                    "example.com",
                    "example.org",
                    "www.example.com",
                    "www.example.edu",
                    "www.example.net"
                ],
                "issuer": "CN=DigiCert Global G2 TLS RSA SHA256 2020 CA1,O=DigiCert Inc,C=US",
                "valid_until": "2025-03-01T23:59:59",
                "valid_from": "2024-01-30T00:00:00"
            }
        ]
    }
}
````

## Examples

Check out the examples in the [examples](examples) folder. They should get you up and running quickly.

## YAML Configuration

### Summary

The tool configuration is done through one or multiple rule configuration files. The file structure is defined in the
[schema file](rules/rules-schema.yml). In addition to some builtin rule types, it is possible to create new types by
registering handlers or rules programmatically.

Rules support registration per DNS record type, as well as batch or any types:

```yaml
plugins:
  - 'sample_module'

storage:
  type: 'dict'
  config: { }

backend:
  type: 'data'
  config:
    'example.com':
      - name: 'example.com'
        type: 'A'
        data: '127.0.0.1'

rules:
  - name: 'Sample'
    type: 'sample'
    record: 'any'

  - name: 'Match digits'
    type: 'regex'
    record: 'A'
    config:
      name: 'TEST'
      regex: '\d+'
      label: 'label'

  - name: 'Add timestamp'
    type: 'timestamp'
    record: 'batch'
  
  - name: 'Mark as test'
    type: 'dynamic'
    record: 'any'
    config:
      code: |
        from dnsmule.utils import extend_set
        
        
        def process(record: Record, result: Result):
            result.data['test'] = True
```

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
  name: 'dnspython'
  config:
    timeout: 5.5
    resolver: 8.8.8.8
```

The backend should extend the `dnsmule.backends.Backend` class or function in a similar way.
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