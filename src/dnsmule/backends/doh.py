from http.client import HTTPSConnection
from json import load
from typing import Iterable
from urllib.parse import urlencode, urlparse

from ..api import Backend, Record, Domain, RRType


class DoHRecord(Record):
    """
    DoH JSON result

    Overrides the text attribute to produce data as the 'data' key from the JSON
    """
    data: dict

    def __init__(self, data: dict):
        super().__init__(
            name=Domain(data['name'].removesuffix('.')),
            type=RRType.from_any(data['type']),
            data=data,
        )

    @property
    def text(self) -> str:
        return self.data['data']


class DoHBackend(Backend):
    """
    Queries DoH JSON endpoints like Google has: https://dns.google/resolve?name=example.com&type=1

    - https://developers.cloudflare.com/1.1.1.1/encryption/dns-over-https/
    - https://developers.google.com/speed/public-dns/docs/doh

    Only config attribute is the URL::

        url <str>   Query endpoint address e.g: https://dns.google/resolve
    """
    type = 'doh'

    def __init__(self, *, url: str):
        super().__init__()
        self.url = url

    def __enter__(self):
        self._url = urlparse(self.url)
        self._client = HTTPSConnection(host=self._url.hostname, port=self._url.port)
        return self

    def __exit__(self, *_):
        self._client.close()
        del self._client

    def scan(self, domain: Domain, *types: RRType) -> Iterable[Record]:
        domain = domain.encode('idna').decode()
        for type in types:
            params = urlencode({
                'name': domain,
                'type': int(type),
            })
            self._client.request('GET', f'{self.url}?{params}')
            response = self._client.getresponse()
            try:
                data = load(response)
                for result in data.get('Answer', []):
                    yield DoHRecord(result)
            finally:
                response.close()
