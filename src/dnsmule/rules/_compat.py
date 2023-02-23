from typing import Any

from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.name import Name


class Domain:
    """Wrapper for dnspython Name
    """
    _wrapped: Name

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, item):
        return getattr(self.data, item)


class Data:
    """Wrapper for dnspython Rdata
    """
    _wrapped: Rdata

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__(self, item):
        return getattr(self._wrapped, item)


class Type:
    """Wrapper for dnspython RdataType
    """
    _wrapped: RdataType

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __hash__(self):
        return hash(self._wrapped)

    def __eq__(self, other):
        return isinstance(other, Type) and other._wrapped == self._wrapped

    def __getattr__(self, item):
        return getattr(self._wrapped, item)

    @classmethod
    def from_text(cls, value: str):
        return cls(_wrapped=RdataType.from_text(value))

    @classmethod
    def from_any(cls, value: Any):
        if isinstance(value, Type):
            return cls(_wrapped=value._wrapped)
        elif isinstance(value, RdataType):
            return cls(_wrapped=value)
        elif isinstance(value, int):
            return cls(_wrapped=RdataType.make(value))
        else:
            return cls.from_text(str(value))


# Set enum members to the wrapper class as well
for k, v in RdataType.__members__.items():
    setattr(Type, k, v)

__all__ = [
    'Data',
    'Type',
    'Domain',
]
