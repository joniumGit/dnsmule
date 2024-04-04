import datetime
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from logging import getLogger
from typing import List, Optional, Dict, cast

from dnsmule import Record, Result
from .iprange import IPvXRange
from .providers import Providers

LOGGER = 'dnsmule.plugins.ipranges'


class IpRangeChecker:
    id = 'ip.ranges'

    _provider_ranges: Dict[str, List[IPvXRange]]
    _last_fetch: Optional[datetime.datetime] = None

    def __init__(
            self,
            *,
            providers: Optional[List[str]] = None,
            interval_hours: int = 10,
    ):
        if providers is not None:
            providers = [*{*providers}]
        else:
            providers = Providers.all()
        for provider in providers:
            if not Providers.available(provider):
                raise KeyError(f'Provider {provider} does not exist')
        self.providers = providers
        self.interval_hours = interval_hours
        self._provider_ranges = cast(Dict[str, List[IPvXRange]], {})

    def __enter__(self):
        self._executor = ThreadPoolExecutor()
        self._executor.__enter__()
        self.check_fetch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._executor.__exit__(exc_type, exc_val, exc_tb)

    def fetch_provider(self, provider: str):
        self._provider_ranges[provider] = Providers.fetch(provider)

    def fetch_ranges(self):
        tasks = []
        for k in self.providers:
            tasks.append(self._executor.submit(self.fetch_provider, k))
        if tasks:
            wait(tasks, return_when=ALL_COMPLETED)
            for t in tasks:
                if t.done() and t.exception() is not None:
                    getLogger(LOGGER).error(
                        'Failed to fetch ranges',
                        exc_info=t.exception(),
                    )

    def check_fetch(self):
        if (
                not self._last_fetch
                or abs(datetime.datetime.now() - self._last_fetch) > datetime.timedelta(hours=self.interval_hours)
        ):
            self.fetch_ranges()
            self._last_fetch = datetime.datetime.now()

    def __call__(self, record: Record, result: Result):
        self.check_fetch()
        address: str = record.text
        for provider, p_ranges in self._provider_ranges.items():
            for p_range in p_ranges:
                if address in p_range:
                    result.tags.add(
                        f'IP::RANGES'
                        f'::{p_range.service.upper()}'
                        f'::{p_range.region.upper()}'
                    )


__all__ = [
    'IpRangeChecker',
]
