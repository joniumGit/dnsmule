# Rules

The tool configuration is done through one or multiple rule configuration files. The file structure is defined in the
[schema file](rules-schema.yml). There are some builtin rule types and it is possible to create new types by registering
handlers programmatically.

It is possible to register rules by files or by creating them programmatically.

Example of programmatic usage (snippet from `dnsmule.backend.dnspython.py`):

```python
def add_ptr_scan(rules: Rules):
    @rules.add.A
    async def ptr_scan(record: Record):
        from dns.rdtypes.IN import A
        from dnsmule.config import get_logger
        og: A = record.data.data['original']
        records = await query_records(reverse_query.from_address(og.to_text()), RdataType.PTR)
        if RdataType.PTR in records:
            for r in records[RdataType.PTR]:
                get_logger().info('PTR %s', r.to_text())
            data: dict = record.result().data
            if 'ptr' not in data:
                data['ptr'] = []
            data['ptr'].extend(r.to_text() for r in records[RdataType.PTR])
```

Any IANA defined DNS record type should work.

## Type Hints and JSON Schema (IntelliJ)

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