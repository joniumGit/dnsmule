"""
This example defines rules in code to implement a simple scanner for TXT and CNAME records

The rules are added directly by registering handlers in code.
It is important to remember to register the Backend implementation as it will default to the NOOPBackend.
The NOOPBackend is usually only useful when testing custom rules or loading rules.
"""

from dnsmule import DNSMule, Record, Rules, DNSPythonBackend, DictStorage, Result
from dnsmule.utils import extend_set, jsonize

mule = DNSMule(
    storage=DictStorage(),
    backend=DNSPythonBackend(),
    rules=Rules()
)


def to_json(result: Result):
    return {
        'name': result.name,
        'types': [*result.types],
        'tags': [*result.tags],
        'data': jsonize(result.data),
    }


@mule.rules.register('CNAME')
def alias_catcher(record: Record, result: Result):
    """
    Adds any CNAME records for a domain into the result

    This can be useful in further analysis as the DNSPythonBackend uses the domain from recursive queries on
    for example A records, which can lead to seemingly "missing" data as it gets attributed to a different domain
    if a CNAME exists for the queried domain.
    """
    extend_set(result.data, 'aliases', record.text)


@mule.rules.register('TXT')
def text_analyzer(record: Record, result: Result):
    """Scans TXT records and matches a predefined list of interesting values
    """
    text_record = record.text
    if any(interesting_value in text_record for interesting_value in [
        'verification',
        'verifier',
        'verify',
        'domain',
        'code',
        'secret',
        'key',
    ]):
        extend_set(result.data, 'records', text_record)
        result.tags.add('INTERESTING')


def analyze(*domains):
    """Analyzes a set of domains and returns the results in a json compatible dict
    """
    mule.scan(*domains)
    storage: DictStorage = mule.storage
    return {
        k: to_json(v)
        for k, v in storage._dict.items()
    }


if __name__ == '__main__':
    import json
    import argparse

    parser = argparse.ArgumentParser(description='searches for interesting TXT records and any CNAME records')
    parser.add_argument('domains', nargs='+', type=str, help='list of domains to scan')
    arguments = parser.parse_args()

    print('Rules:  ', *mule.rules.all)
    print('Results:', json.dumps(
        analyze(*arguments.domains),
        ensure_ascii=False,
        indent=4,
    ))
