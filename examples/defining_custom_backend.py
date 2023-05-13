"""
This example defines a pooled backend that uses multiple DNSPython backends to run queries

This can make queries faster
"""

from typing import Iterable, List

from dnsmule.backends import Backend
from dnsmule.backends.dnspython import DNSPythonBackend
from dnsmule.definitions import Record, RRType, Domain
from dnsmule.logger import get_logger


class PooledBackend(Backend):
    """Allows using a pool of resolvers
    """
    resolvers: List[str]

    def __init__(self, **kwargs):
        from queue import Queue
        from multiprocessing.pool import ThreadPool
        super(PooledBackend, self).__init__(**kwargs)
        self.pool = ThreadPool(processes=len(self.resolvers))
        self.querier_pool = Queue(maxsize=len(self.resolvers))
        for item in [
            DNSPythonBackend(**self._kwargs, resolver=resolver)
            for resolver in self.resolvers
        ]:
            self.querier_pool.put(item, block=True)

    def __del__(self):
        self.pool.close()
        self.pool.join()

    def run(self, targets: Iterable[Domain], *types: RRType) -> Iterable[Record]:
        items = [
            item
            for result_partition in self.pool.starmap(
                self._query, ((target, rtype) for target in targets for rtype in types)
            )
            for item in result_partition
        ]
        yield from items

    def single(self, target: Domain, *types: RRType) -> Iterable[Record]:
        yield from self.run([target], *types)

    def _query(self, target: Domain, *types: RRType) -> Iterable[Record]:
        querier: DNSPythonBackend = self.querier_pool.get(block=True)
        get_logger().info('Loaned %s', id(querier))
        try:
            get_logger().info('Starting %s', target)
            yield from querier.single(target, *types)
            get_logger().info('Done with %s', target)
        finally:
            self.querier_pool.put(querier, block=True)
            get_logger().info('Returned %s', id(querier))


__all__ = [
    'PooledBackend',
]
