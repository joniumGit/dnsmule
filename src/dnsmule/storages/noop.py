from typing import Optional

from ..api import Storage, Result, Domain


class NoOpStorage(Storage):
    """Does nothing
    """
    type = 'noop'

    def fetch(self, domain: Domain) -> Optional[Result]:
        return None

    def store(self, result: Result) -> None:
        """Discards all results
        """
