import asyncio
import contextlib
import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Dict

from dnsmule.config import get_logger
from dnsmule.definitions import Record, Result
from dnsmule.rules import DynamicRule
from . import ranges


class IpRangeChecker(DynamicRule):
    providers: List[str]

    _last_fetch: Optional[datetime.datetime] = None
    _provider_ranges: Dict[str, List[ranges.IPvXRange]]
    _task: asyncio.Task

    def __init__(self, **kwargs):
        kwargs['code'] = 'pass'
        super().__init__(**kwargs)
        self.globals = {}
        self.providers = [*{*self.providers}] if hasattr(self, 'providers') else []
        self._provider_ranges = {}
        for provider in self.providers:
            # If this fails it will throw
            self._get_fetcher(provider)

    def update_fetched(self, *_, **__):
        self._last_fetch = datetime.datetime.now()
        del self._task

    def start_fetching(self):
        self._task = asyncio.create_task(self.fetch_ranges())
        self._task.add_done_callback(self.update_fetched)

    def init(self, *_, **__):
        try:
            self.start_fetching()
        except RuntimeError:
            """No Loop running
            """

    @staticmethod
    def _get_fetcher(provider: str):
        return getattr(ranges, f'fetch_{provider}_ip_ranges')

    def fetch_provider(self, provider: str):
        self._provider_ranges[provider] = self._get_fetcher(provider)()

    async def fetch_ranges(self):
        with ThreadPoolExecutor() as tp:
            tasks = []
            loop = asyncio.get_running_loop()
            for k in self.providers:
                tasks.append(loop.run_in_executor(tp, self.fetch_provider, k))
            if tasks:
                try:
                    await asyncio.gather(*tasks, return_exceptions=False)
                except Exception as e:
                    coro = asyncio.gather(*tasks, return_exceptions=True)
                    coro.cancel()
                    with contextlib.suppress(asyncio.TimeoutError, asyncio.CancelledError):
                        await coro
                    get_logger().error('Failed to fetch ranges', exc_info=e)

    async def check_fetch(self):
        if hasattr(self, '_task'):
            await self._task
        elif not self._last_fetch or abs(datetime.datetime.now() - self._last_fetch) > datetime.timedelta(hours=1):
            self.start_fetching()
            await self._task

    async def __call__(self, record: Record) -> Result:
        await self.check_fetch()
        result = record.result()
        address: str = record.data.to_text()
        for provider, p_ranges in self._provider_ranges.items():
            for p_range in p_ranges:
                if address in p_range:
                    result.tags.add(
                        f'IP::RANGES'
                        f'::{self.name.upper()}'
                        f'::{p_range.service.upper()}'
                        f'::{p_range.region.upper()}'
                    )
        return result


__all__ = [
    'IpRangeChecker',
]
