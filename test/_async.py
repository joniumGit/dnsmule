import asyncio
from functools import wraps


def async_test(test_function):
    @wraps(test_function)
    def run_test(*args, **kwargs):
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(test_function(*args, **kwargs))
        finally:
            loop.close()

    return run_test


__all__ = [
    'async_test',
]
