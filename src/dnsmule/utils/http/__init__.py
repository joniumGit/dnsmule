try:
    from . import certificates
    from . import ranges
except ImportError as e:
    from ...config import get_logger

    get_logger().critical('Required dependencies not available', exc_info=e)
    raise
