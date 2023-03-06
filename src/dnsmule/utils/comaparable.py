SORT_KEY = '_sort_key'


class ComparisonMixinBase:
    _sort_key: str

    def __lt__(self, other):
        return self._sort_key < other._sort_key

    def __gt__(self, other):
        return self._sort_key > other._sort_key

    def __ge__(self, other):
        return self._sort_key >= other._sort_key

    def __le__(self, other):
        return self._sort_key <= other._sort_key


class Comparable(type):
    def __new__(mcs, name, bases, attrs, key: str = None, reverse: bool = False):
        if not key:
            if any(map(lambda b: isinstance(b, Comparable), bases)):
                return super().__new__(
                    mcs,
                    name,
                    bases,
                    attrs,
                )
            raise ValueError('nothing to compare by')

        if reverse:
            class ComparisonMixin(ComparisonMixinBase):
                def __getattr__(self, item):
                    if item == SORT_KEY:
                        return -getattr(self, key)
                    raise AttributeError(f'{type(self)}: {item}')
        else:
            class ComparisonMixin(ComparisonMixinBase):
                def __getattr__(self, item):
                    if item == SORT_KEY:
                        return getattr(self, key)
                    raise AttributeError(f'{type(self)}: {item}')

        instance = super().__new__(
            mcs,
            name,
            (*bases, ComparisonMixin),
            attrs,
        )

        return instance


__all__ = [
    'Comparable'
]
