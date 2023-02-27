from typing import Any

from dns.rdata import Rdata
from dns.rdatatype import RdataType, to_text as type_to_text
from dns.name import Name


class CopyCat:

    def __init__(self, _wrapped):
        self._wrapped = _wrapped

    def __getattr__(self, item):
        if item != '_wrapped':
            return getattr(self._wrapped, item)

    def __hash__(self):
        return self._wrapped.__hash__()

    def __eq__(self, other):
        if other is self:
            return True
        elif isinstance(other, CopyCat):
            return self._wrapped.__eq__(other._wrapped)
        else:
            return self._wrapped.__eq__(other)

    def unwrap(self):
        return self._wrapped

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self._wrapped.__repr__()


for method in ['__lt__', '__gt__', '__ge__', '__le__', ]:
    def _method(self, other):
        if isinstance(other, CopyCat):
            return getattr(self._wrapped, method)(other._wrapped)
        else:
            return getattr(self._wrapped, method)(other)


    _method.__name__ = method

    setattr(CopyCat, method, _method)


class Domain(CopyCat):
    """Wrapper for dnspython Name
    """
    _wrapped: Name

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self._wrapped.to_text(omit_final_dot=True)


class Data(CopyCat):
    """Wrapper for dnspython Rdata
    """
    _wrapped: Rdata

    def unwrap(self):
        return self._wrapped

    def to_text(self, *args, **kwargs):
        """Returns the value with string quotes removed
        """
        return self._wrapped.to_text(*args, **kwargs).removeprefix('"').removesuffix('"')

    def __str__(self):
        return self.to_text()


class Type(CopyCat):
    """Wrapper for dnspython RdataType
    """
    _wrapped: RdataType

    def __int__(self):
        return self._wrapped.__int__()

    def __str__(self):
        return type_to_text(self._wrapped)

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
    setattr(Type, k, Type(_wrapped=v))

__all__ = [
    'Data',
    'Type',
    'Domain',
]
