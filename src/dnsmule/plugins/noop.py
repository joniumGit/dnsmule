from .abstract import Plugin


class NOOPPlugin(Plugin):
    """NOOP
    """
    id = 'plugin.noop'

    def register(self, _):
        """NOOP
        """


__all__ = [
    'NOOPPlugin'
]
