"""
Contains all ip address range fetchers

These all have only one method::

    provider.fetch()


"""
from . import (
    amazon,
    digitalocean,
    google,
    microsoft,
    cloudflare,
    # Add here so the provider is registered
)
from ._core import Providers

__all__ = [
    'Providers',
]
