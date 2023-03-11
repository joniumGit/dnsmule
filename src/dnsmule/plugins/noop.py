from .abstract import Plugin


class NOOPPlugin(Plugin):
    """NOOP
    """

    def register(self, _):
        """NOOP
        """


__all__ = [
    'NOOPPlugin'
]
