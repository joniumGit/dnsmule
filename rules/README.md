# Rules

#### Summary

The tool configuration is done through one or multiple rule configuration files. The file structure is defined in the
[schema file](rules-schema.yml). In addition to some builtin rule types, it is possible to create new types by
registering handlers or rules programmatically.

Rules support registration per DNS record type and priority for controlling invocation order.

```yaml
version: '0.0.1'
rules:
  - o365:
    priority: 10
    type: dns.regex
    record: txt
    pattern: '^MS=ms'
    identification: MICROSOFT::O365
  - ses:
    type: dns.regex
    record: txt
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
async def my_scan(record: Record) -> Result:
    from dnsmule.config import get_logger
    get_logger().info('Address %s', record)
    return record.identify('MY::SCAN')


@rules.register('my.rule')
def create_my_rule(**arguments) -> Rule:
    ...
```

Here the `add` is used to directly register a new rule into the ruleset with a given priority. The `register` call
creates a new handler for rules of type `my.rule`. Any future `my.rule` creations from `yml` or code would be routed to
this factory function.

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
    from dnsmule.rules.entities import Type, Record, Result

    def add_rule(record_type: Any, rule_type: str, name: str, priority: int = 0, **options) -> None:
        pass

  suffix: ''
```

Currently, this supports `dns.regex` pattern regex language injection and `dns.dynamic` rule code language injection.
Type hints and quick documentation are available.

## Builtin types

#### Regex rules

Regex rules can be defined with either one `pattern` or multiple `patterns`.
An example is in the following snippet:

```yml
rules:
  - test:
    type: dns.regex
    record: txt
    pattern: '^.*\.hello_world\.'
    identification: HELLO::WORLD
    flags:
      - UNICODE
      - DOTALL
  - generic_verification:
    type: dns.regex
    record: txt
    priority: 10
    name: Generic Site Regex Collection
    patterns:
      - '^(.+)(?:-(?:site|domain))?-verification='
      - '^(.+)(?:site|domain)verification'
      - '^(.+)_verify_'
      - '^(\w+)-code:'
    group: 1
```

The full definition is available from the schema file.

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
        record_type: Any,
        rule_type: str,
        name: str,
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
    pass
```

The only globals passed to these methods are:

- \_\_builtins\_\_
- from dnsmule.definitions import RRType, Record, Result, Rule, DynamicRule
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