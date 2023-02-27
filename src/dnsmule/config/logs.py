import logging


def get_logger():
    return logging.getLogger('dnsmule')


__all__ = [
    'get_logger'
]
