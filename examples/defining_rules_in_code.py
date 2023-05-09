"""
This example defines rules in code to implement a simple scanner for TXT and CNAME records

The rules are added directly by registering handlers in code.
It is important to remember to register the Backend implementation as it will default to the NOOPBackend.
The NOOPBackend is usually only useful when testing custom rules or loading rules.
"""

from dnsmule import DNSMule, Record
from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.storages.abstract import result_to_json_data
from dnsmule.storages.dictstorage import DictStorage
from dnsmule.utils import extend_set

mule = DNSMule.make(
    storage=DictStorage(),
    backend=DNSPythonBackend(),
)


@mule.rules.add.CNAME
def alias_catcher(record: Record):
    """
    Adds any CNAME records for a domain into the result

    This can be useful in further analysis as the DNSPythonBackend uses the domain from recursive queries on
    for example A records, which can lead to seemingly "missing" data as it gets attributed to a different domain
    if a CNAME exists for the queried domain.
    """
    extend_set(record.result.data, 'aliases', [record.text])


@mule.rules.add.TXT
def text_analyzer(record: Record):
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
        extend_set(record.result.data, 'records', [text_record])
        record.tag('INTERESTING')


def analyze(*domains):
    """Analyzes a set of domains and returns the results in a json compatible dict
    """
    mule.scan(*domains)
    return {
        k: result_to_json_data(v)
        for k, v in mule.storage.items()
    }


if __name__ == '__main__':
    import json
    import argparse

    parser = argparse.ArgumentParser(description='searches for interesting TXT records and any CNAME records')
    parser.add_argument('domains', nargs='+', type=str, help='list of domains to scan')
    arguments = parser.parse_args()

    print('Rules:  ', *mule.rules)
    print('Results:', json.dumps(
        analyze(*arguments.domains),
        ensure_ascii=False,
        indent=4,
    ))
