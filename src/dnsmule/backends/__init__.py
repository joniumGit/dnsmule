from .csvfile import CSVBackend
from .data import DataBackend
from .doh import DoHBackend
from .noop import NoOpBackend

try:
    from .dnspython import DNSPythonBackend
except ImportError:
    """Fails to load if there is no dep installed
    """
    from logging import getLogger

    getLogger('dnsmule').debug('DNSPython not available')
