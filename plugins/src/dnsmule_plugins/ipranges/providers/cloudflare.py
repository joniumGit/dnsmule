from typing import List

from ._core import Providers, fetch_text, IPvXRange

CLOUDFLARE_IPV4 = 'https://www.cloudflare.com/ips-v4'
CLOUDFLARE_IPV6 = 'https://www.cloudflare.com/ips-v6'


@Providers.register('cloudflare')
def fetch() -> List[IPvXRange]:
    return [
        IPvXRange.create(
            address=address,
            region='GLOBAL',
            service='CLOUDFLARE',
        )
        for address in (
                fetch_text(CLOUDFLARE_IPV4, add_agent=True).splitlines(keepends=False)
                + fetch_text(CLOUDFLARE_IPV6, add_agent=True).splitlines(keepends=False)
        )
    ]
