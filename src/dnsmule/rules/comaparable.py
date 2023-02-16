class ComparisonMixinBase:
    __sort_key__: str

    def __lt__(self, other):
        return self.__sort_key__ < other.__sort_key__

    def __gt__(self, other):
        return self.__sort_key__ > other.__sort_key__

    def __ge__(self, other):
        return self.__sort_key__ >= other.__sort_key__

    def __le__(self, other):
        return self.__sort_key__ <= other.__sort_key__


class Comparable(type):
    def __new__(mcs, name, bases, attrs, key: str = None, reverse: bool = False):
        if not key:
            raise ValueError('nothing to compare by')

        if reverse:
            class ComparisonMixin(ComparisonMixinBase):
                def __getattribute__(self, item):
                    if item == '__sort_key__':
                        return -getattr(self, key)
                    else:
                        return super().__getattribute__(item)
        else:
            class ComparisonMixin(ComparisonMixinBase):
                def __getattribute__(self, item):
                    if item == '__sort_key__':
                        return getattr(self, key)
                    else:
                        return super().__getattribute__(item)

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
