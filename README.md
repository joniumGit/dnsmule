# DNSMule

[![codecov](https://codecov.io/gh/joniumGit/dnsmule/branch/master/graph/badge.svg?token=54DPREJIFU)](https://codecov.io/gh/joniumGit/dnsmule)

Package for rule based dependency scanning and service fingerprinting via DNS.

This package provides utilities for writing and evaluating verbose and easy to read rule definitions in YAML-format.
There some builtin rule formats with more available as plugins.

## Note: 0.8.0 is not compatible with 0.5.0

Due to needing the implementation to be less bloated, teh structure was changed.
There is now much less code and useless features were removed.

Here is the gist:

- The API has been slimmed down
    - Almost no "hacked" attributes
        - Only the `context` is "injected" into rules when processing
        - Context contains `mule`, `rules`, `storage` and `backend`
    - Record has had its `result` property removed
    - Record has been simplified
    - Everything is now optionally a context manager
        - Allows easy initialization and de-initialization
        - Storage, Mule and Backend are entered together
        - Rules are entered once per scan
    - Rules were reworked to be simple callables
        - New signature `__call__(Record, Result) -> None`
        - Scan result is now explicitly given to the rule
        - Result is modified by the rule and nothing is returned to reduce complexity
        - Removed rule priority
            - Now simply respects insertion order
        - Added batch rules
            - Signature `__call__(List[Record], Result) -> None`
            - Batches are run at the end of processing
        - Added ANY matching rules
            - Will get called using all produced records
            - Note: Only record types with active rules are scanned
        - Created additional built-in rule types
        - Storage was slimmed down
            - Now a storage simply has `store` and `fetch`
            - Additional storage types for databses
        - Backends were simplified
            - Added some utility backends
- Redesigned the YAML loader and Plugin handling
    - Now there is no hacky loading going on
    - Plugins are implicit and do no hooking
    - Plugins only extend rule, storage and backend type scan options
- Example server was removed completely
    - Did not have time to rewrite it yet
    - Nearly useless without search
- Adds a command line runner for rules (WIP)

## Installation

```shell
pip install dnsmule[full] dnsmule_plugins[full]
```

This will install everything available for DNSMule. You can also choose to install components as necessary.

For installing from the repo you can use:

```shell
pip install -e . ./plugins
```

## Overview

The DNSMule tool takes YAML config as input and uses it to scan a domain:

```shell
python -m dnsmule --config rules/rules.yml example.com
```

This will give output like:

````json
{
  "name": "example.com",
  "types": [
    "TXT",
    "A"
  ],
  "tags": [],
  "data": {}
}
````

## Examples

Check out the examples in the [examples](examples) folder.
They should get you up and running quickly.
The examples show some of the features available in DNSMule.

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

## Dynamic Rules

Dynamic rules are defined as code snippets with one or two methods

An init method that is invoked once after creation

```python
def init() -> None:
    ...
```

A process function that is invoked once for each record

```python
def process(record: Record, result: Result) -> None:
    ...
```

The only globals passed to these methods are:

- \_\_builtins\_\_
- RRType, Record, Result, Domain, Config
    - The Config contains the `config` property passed to the rule from YAML
- Any additional globals created by the code itself

When the code is exec'd the result is inspected for:

- init function
- process function

Some notes:

- The init function is invoked every time the rule context is entered
    - Take note that this happens on every scan
- The process function is invoked exactly once for a single Record
- Any rules created from the init method will be invoked for every suitable record

## Notice

This package is under development.
Pull requests are welcome, but will only be accepted after 0.8.0 is complete and my thesis is done.