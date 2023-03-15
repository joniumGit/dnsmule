# Plugins for DNSMule

It is recommended to look through each module to see what arguments they take.

#### Certcheck

Arguments:

```yaml
rules:
  - name: certcheck
    record: A
    type: 'ip.certs'
    config:
      ports: # Ports to scan
        - 443
        - 8443
      timeout: 1 # timeout for cert fetching
      stdlib: false # Prefer STDLIB implementation
      callback: false # Whether a callback should be called for resolved domains
```

Scans any resolved `A` or `AAAA` record for certificates from a given list of ports.
There are two ways to scan for certificates, a Python stdlib solution and one with `cryptography` library parsing certs.

Tags are produced for cert issuer:

```text
IP::CERTS::{rule_name}::ISSUER::{issuer_rfc_string}
```

More data is available in `result.data`:

```python
result.data['resolvedCertificates'] = certificates_as_list_of_dicts
```

See the `Certificate` dataclass `to_json` method in [certificates.py](src/dnsmule_plugins/certcheck/certificates.py).

The plugin takes a callback argument for any domains resolved from certificate common and alternative names.

This plugin requires the following dependencies:

- `cryptography` (optional)

#### IPRanges

Arguments:

```yaml
rules:
  - name: ipranges
    record: A
    type: 'ip.ranges'
    config:
      providers: # Lowercase only
        - amazon
        - google
        - microsoft
```

Scans any resolved `A` or `AAAA` record for addresses in the major cloud provider ranges.
Currently, supports the following providers:

- Microsoft
- Google Cloud
- Amazon AWS

Provider IP ranges are refreshed on one hour intervals.

This provides tags like:

```text
IP::RANGES::{rule_name}::{provider}::{service}::{region}
IP::RANGES::SAMPLE_RULE::AMAZON::LAMBDA::US-WEST-1
```

This plugin requires the following dependencies:

- `httpx`

#### PTRScan

Arguments:

```yaml
rules:
  - name: ptrscan
    record: A
    type: 'ip.ptr'
```

Scans any resolved `A` or `AAAA` record for a matching `PTR` record.
The pointer is used to discover automatically generated cloud provider pointer records for services.
The plugin tries to detect pointer records where the ip of the `A` or `AAAA` record is present in any of the following
forms:

- dot separated
- dot separated reversed
- dash separated
- dash separated reversed
- Any of the above anywhere in the string

This resolves to a provider with the prefix removed from the record.

For example a `PTR` of the form with a rule name `sample_rule`

```text
123.456.789.000 IN PTR CDN-123-456-789-000.area.hoster.example.com
```

would produce a tag of the form

```text
IP::PTR::SAMPLE_RULE::AREA.HOSTER.EXAMPLE.COM
```

Any resolved `PTR` records are also added to `result.data['resolvedPointers']`.

## Example

In YAML the plugins are placed in their own `plugins` block:

```yaml
plugins:
  - name: dnsmule_plugins.PTRScanPlugin
  - name: dnsmule_plugins.IPRangesPlugin
  - name: dnsmule_plugins.CertCheckPlugin
    config:
      callback: false
```

Here is an example of how to add a ruleset containing all plugins to a `DNSMule` instance.

```python
from dnsmule import DNSMule, RRType, Rules
from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.loader import load_and_append_rule
from dnsmule_plugins import certcheck, ipranges, ptrscan

mule = DNSMule.make(Rules(), DNSPythonBackend())

certcheck.CertCheckPlugin(callback=False).register(mule)
ipranges.IPRangesPlugin().register(mule)

load_and_append_rule(
    mule.rules,
    RRType.A,
    'ip.certs',
    {
        'name': 'certcheck',
    },
)

load_and_append_rule(
    mule.rules,
    RRType.A,
    'ip.ranges',
    {
        'name': 'ipranges',
        'providers': [
            'amazon',
            'microsoft',
            'google',
        ]
    },

)

ptrscan.PTRScanPlugin().register(mule)
load_and_append_rule(
    mule.rules,
    RRType.A,
    'ip.ptr',
    {
        'name': 'ptrscan'
    },
)
```
