import os
from random import choice

DEFAULT_RESOLVER = os.getenv('DNSMULE_RESOLVER', choice([
    '208.67.222.222',
    '208.67.220.220',
    '1.1.1.1',
    '1.0.0.1',
    '8.8.8.8',
    '8.8.4.4',
]))

__all__ = [
    'DEFAULT_RESOLVER',
]
