from html.parser import HTMLParser
from typing import List

from ._core import fetch_json, fetch_text, IPvXRange, Providers

JSON_DOWNLOAD_PREFIX = 'https://download.microsoft.com'
ASPX_DOWNLOAD_URL = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=%s'
ASPX_IDS = [
    56519,  # Azure Public
    57063,  # US Government
    57062,  # China 21Vianet
    57064,  # Azure Germany
]
ASPX_CATALOGUE = [
    'PUBLIC',
    'USGOV',
    'CHINA',
    'GERMANY',
]


class MicrosoftDownloadGrabber(HTMLParser):
    json_url: str = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'a':
            attrs = {k: v for k, v in attrs}
            if attrs.get('href', '').startswith(JSON_DOWNLOAD_PREFIX):
                if self.json_url is None:
                    self.json_url = attrs['href']


def scrape_ranges_json(url: str) -> dict:
    p = MicrosoftDownloadGrabber()
    p.feed(fetch_text(url))
    return fetch_json(p.json_url)


@Providers.register('microsoft')
def fetch(drop_unknowns=False) -> List[IPvXRange]:
    return [
        IPvXRange.create(
            address=address,
            region=f'{entry["properties"]["region"] or "UNKNOWN"}'.upper(),
            service=f'MICROSOFT::{entry["properties"]["systemService"] or "UNKNOWN"}::{catalogue}'.upper(),
        )
        for catalogue, document_id in zip(ASPX_CATALOGUE, ASPX_IDS)
        for entry in scrape_ranges_json(ASPX_DOWNLOAD_URL % document_id)['values']
        for address in entry['properties']['addressPrefixes']
        if not drop_unknowns or entry['properties']['systemService'] and entry['properties']['region']
    ]
