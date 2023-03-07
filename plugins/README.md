# Plugins for DNSMule

It is recommended to look through each module to see what arguments they take.

#### Certcheck

Arguments:

```yaml
rules:
  - certcheck:
    record: A
    type: 'ip.certs'
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
  - ipranges:
    record: A
    type: 'ip.ranges'
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
  - ptrscan:
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

This plugin requires the following dependencies:

- `dnspython`
- `dnsmule.backends.DNSPythonBackend`

## Example

Here is an example of how to add a ruleset containing all plugins to a `DNSMule` instance.
This will change in the future when a `plugins` directive is supported in the `rules.yml` config.

```python
import os

from dnsmule import DNSMule
from dnsmule.rules.utils import load_rules
from dnsmule_plugins import certcheck, ipranges

mule = DNSMule.load(os.getenv('MULE_CONFIG'))

certcheck.plugin_certcheck(mule.rules, lambda ds: mule.store_domains(*ds))
ipranges.plugin_ipranges(mule.rules)

load_rules([
    {
        'record': 'A',
        'type': 'ip.certs',
        'name': 'certcheck',
    },
    {
        'record': 'A',
        'type': 'ip.ranges',
        'name': 'ipranges',
        'providers': [
            'amazon',
            'microsoft',
            'google',
        ]
    },
], rules=mule.rules)

if mule.backend == 'DNSPythonBackend':
    from dnsmule_plugins import ptrscan

    ptrscan.plugin_ptr_scan(mule.rules, mule.get_backend())
    load_rules([
        {
            'record': 'A',
            'type': 'ip.ptr',
            'name': 'ptrscan',
        },
    ], rules=mule.rules)
```