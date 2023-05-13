from itertools import chain
from typing import List

from ._core import IPvXRange, fetch_json, Providers

AWS_URL = 'https://ip-ranges.amazonaws.com/ip-ranges.json'


@Providers.register('amazon')
def fetch() -> List[IPvXRange]:
    data = fetch_json(AWS_URL)
    return [
        IPvXRange.create(
            address=e['ip_prefix'] if 'ip_prefix' in e else e['ipv6_prefix'],
            region=e['region'],
            service=f'AMAZON::{e["service"] or "UNKNOWN"}'.upper(),
        )
        for e in chain(data['prefixes'], data['ipv6_prefixes'])
    ]
