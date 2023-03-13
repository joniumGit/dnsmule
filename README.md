# DNSMule

[![codecov](https://codecov.io/gh/joniumGit/dnsmule/branch/master/graph/badge.svg?token=54DPREJIFU)](https://codecov.io/gh/joniumGit/dnsmule)

Package for rule based dependency scanning and service fingerprinting via DNS.

This package provides utilities for writing and evaluating verbose and easy to read rule definitions in _YAML_-format.
There are two builtin rule formats with more available as plugins.

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