from typing import List

from ._core import IPvXRange, fetch_text, Providers

DO_URL = 'https://digitalocean.com/geo/google.csv'


@Providers.register('digitalocean')
def fetch() -> List[IPvXRange]:
    data = fetch_text(DO_URL, add_agent=True)
    out = []
    for line in data.splitlines(keepends=False):
        ip, _, region, *_ = map(str.strip, line.split(','))
        out.append(IPvXRange.create(
            address=ip,
            region=region,
            service='DIGITALOCEAN',
        ))
    return out
