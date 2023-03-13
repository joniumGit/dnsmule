# DNSMule

[![codecov](https://codecov.io/gh/joniumGit/dnsmule/branch/master/graph/badge.svg?token=54DPREJIFU)](https://codecov.io/gh/joniumGit/dnsmule)

Package for rule based dependency scanning and service fingerprinting via DNS.

This package provides utilities for writing and evaluating verbose and easy to read rule definitions in _YAML_-format.
There are two builtin rule formats with more available as plugins.

#### Current State

States (Complete, Testing, Developing, Refining) for every feature planned at this moment.

- Backends (Complete)
    - DNSPythonBackend
    - YAML definition
- Rules (Testing)
    - Builtin types
    - Custom rules
    - Custom rule factories
    - YAML definition (Complete)
- Plugins (Developing)
    - Registration in program (Developing)
    - Registration in YAML (Refining)
    - YAML definition (Refining)
- DNSMule (Developing)
    - Rules from YAML (Complete)
    - Backend from YAML (Complete)
    - Processing and gathering results (Testing)
    - Plugins from YAML (Refining)
    - Result storage (Refining)
    - Combined YAML definition (Refining)

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