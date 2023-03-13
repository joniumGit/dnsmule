# DNSMule

[![codecov](https://codecov.io/gh/joniumGit/dnsmule/branch/master/graph/badge.svg?token=54DPREJIFU)](https://codecov.io/gh/joniumGit/dnsmule)

Package for rule based dependency scanning and service fingerprinting via DNS.

This package provides utilities for writing and evaluating verbose and easy to read rule definitions in _YAML_-format.
There are two builtin rule formats with more available as plugins.

## Overview

The DNSMule tool is composed in the following way:

- DNSMule
    - Backend
    - Rules
        - Rule
    - Plugins

#### Backends

Any backend can be used and registered in YAML, the only requirement is extending the `dnsmule.backends.Backend` class.
A backend is responsible for creating `dnsmule.definition.Record` instances for processing with `dnsmule.rules.Rules`.

#### Plugins

Plugins provide DNSMule with additional functionality and/or rule(types).
Plugins can be registered in YAML.
It is required that all plugins extend the `dnsmule.plugins.Plugin` class.

#### Rules

This class is responsible for processing every`Record` and producing a `dnsmule.definition.Result` for them.
The actual processing happens in individual `dnsmule.rules.Rule` instances that are ordered and orchestrated by this
class.

#### Rule

These are user defined rules that process individual `Record` instances and append information to `record.data`
or `record.tags`. The `record.data` is a storage for result metadata and additional information. The `record.tags` set
is a collection of identifications for an input `Record`.

#### Current State

States (Complete, Testing, Developing, Refining) for every feature planned at this moment.

- (Complete) Backends
    - (Complete) DNSPythonBackend
    - (Complete) YAML definition
- (Complete) Rules
    - (Complete) Builtin types
    - (Complete) Custom rules
    - (Complete) Custom rule factories
    - (Complete) YAML definition
- (Testing) Plugins
    - (Complete) Registration in program
    - (Complete) Registration in YAML
    - (Complete) YAML definition
    - (Developing) Increasing test coverage
- (Refining) Result Storage
    - (Refining) Registration in program
    - (Refining) Registration in YAML
    - (Refining) YAML definition
- (Developing) DNSMule
    - (Complete) Rules from YAML
    - (Complete) Backend from YAML
    - (Testing) Plugins from YAML
    - (Developing) Processing and gathering results
    - (Refining) Result storage
    - (Refining) Result storage from YAML
    - (Refining) Combined YAML definition

#### Example server

The repo has a `Dockerfile` for easily running the tool using an example server in Docker:

```shell
$ ./build-image
$ ./run-server
```

#### Notice

This package is under active development.

#### Additional

- RnD Scripts under [scripts](scripts)
- Example server under [server](server) 