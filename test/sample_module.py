from dnsmule import Record, Result


class Sample:
    type = 'sample'

    def __call__(self, _: Record, result: Result):
        result.tags.add('SAMPLE')


__all__ = [
    'Sample',
]
