import asyncio
import datetime
from typing import List, Optional, Dict

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

    def update_fetched(self, *_, **__):
        self._last_fetch = datetime.datetime.now()
        del self._task

    def start_fetching(self):
        self._task = asyncio.create_task(self.fetch_ranges())
        self._task.add_done_callback(self.update_fetched)

    def init(self, *_, **__):
        self.start_fetching()

    async def fetch_provider(self, provider: str):
        if provider not in self._provider_ranges:
            self._provider_ranges[provider] = await asyncio.create_task(
                getattr(ranges, f'fetch_{provider}_ip_ranges')())

    async def fetch_ranges(self):
        tasks = []
        for k in self.providers:
            tasks.append(asyncio.create_task(self.fetch_provider(k)))
        try:
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        except:
            coro = asyncio.gather(*tasks)
            coro.cancel()
            try:
                await coro
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            raise

    async def check_fetch(self):
        if hasattr(self, '_task'):
            await self._task
        elif not self._last_fetch or abs(datetime.datetime.now() - self._last_fetch) > datetime.timedelta(hours=1):
            self._provider_ranges.clear()
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
