import asyncio
import datetime
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from typing import List, Optional, Dict, cast

from dnsmule.definitions import Record, Result
from dnsmule.logger import get_logger
from dnsmule.rules import Rule
from . import ranges


class IpRangeChecker(Rule):
    id = 'ip.ranges'

    providers: List[str]

    _last_fetch: Optional[datetime.datetime] = None
    _provider_ranges: Dict[str, List[ranges.IPvXRange]]
    _task: asyncio.Task

    def __init__(self, **kwargs):
        kwargs['code'] = 'pass'
        super().__init__(**kwargs)
        self.globals = {}
        self.providers = [*{*self.providers}] if hasattr(self, 'providers') else []
        self._provider_ranges = cast(Dict[str, List[ranges.IPvXRange]], {})
        for provider in self.providers:
            # If this fails it will throw
            self._get_fetcher(provider)

    @staticmethod
    def _get_fetcher(provider: str):
        return getattr(ranges, f'fetch_{provider}_ip_ranges')

    def fetch_provider(self, provider: str):
        self._provider_ranges[provider] = self._get_fetcher(provider)()

    def fetch_ranges(self):
        with ThreadPoolExecutor() as tp:
            tasks = []
            for k in self.providers:
                tasks.append(tp.submit(self.fetch_provider, k))
            if tasks:
                wait(tasks, return_when=ALL_COMPLETED)
                for t in tasks:
                    if t.done() and t.exception() is not None:
                        get_logger().error('Failed to fetch ranges', exc_info=t.exception())

    def check_fetch(self):
        if not self._last_fetch or abs(datetime.datetime.now() - self._last_fetch) > datetime.timedelta(hours=1):
            self.fetch_ranges()
            self._last_fetch = datetime.datetime.now()

    def __call__(self, record: Record) -> Result:
        self.check_fetch()
        address: str = record.text
        for provider, p_ranges in self._provider_ranges.items():
            for p_range in p_ranges:
                if address in p_range:
                    record.result.tags.add(
                        f'IP::RANGES'
                        f'::{self.name.upper()}'
                        f'::{p_range.service.upper()}'
                        f'::{p_range.region.upper()}'
                    )
        return record.result


__all__ = [
    'IpRangeChecker',
]
