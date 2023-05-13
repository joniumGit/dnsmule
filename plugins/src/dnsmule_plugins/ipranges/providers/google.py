from typing import List

from ._core import IPvXRange, fetch_json, Providers

GOOG_URL = 'https://www.gstatic.com/ipranges/goog.json'
CLOUD_URL = 'https://www.gstatic.com/ipranges/cloud.json'


def fetch_google_ip_ranges_goog() -> List[IPvXRange]:
    return [
        IPvXRange.create(
            address=e[k],
            region='GLOBAL',
            service='GOOGLE::GOOGLE',
        )
        for e in fetch_json(GOOG_URL)['prefixes']
        for k in e.keys() if k.endswith('Prefix')
    ]


def fetch_google_ip_ranges_cloud() -> List[IPvXRange]:
    return [
        IPvXRange.create(
            address=e[k],
            region=e['scope'],
            service=f'GOOGLE::{e["service"] or "GENERIC"}'.upper(),
        )
        for e in fetch_json(CLOUD_URL)['prefixes']
        for k in e.keys() if k.endswith('Prefix')
    ]


@Providers.register('google')
def fetch():
    return [
        *fetch_google_ip_ranges_cloud(),
        *fetch_google_ip_ranges_goog(),
    ]
