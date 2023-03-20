from .abstract import Plugin


class NOOPPlugin(Plugin):
    """NOOP
    """
    _id = 'plugin.noop'

    def register(self, _):
        """NOOP
        """


__all__ = [
    'NOOPPlugin'
]
