from typing import Iterable, Optional

from pymongo import MongoClient

from .abstract import Storage, result_from_json_data, result_to_json_data, Query, DefaultQuerier
from .. import Result, Domain, RRType


class MongoDB(Storage):
    database: str = 'dnsmule'
    collection: str = 'results'

    def __init__(self, **kwargs):
        super(MongoDB, self).__init__(**kwargs)
        self._client = MongoClient(**{
            k: getattr(self, k)
            for k in self._properties
            if k != 'database' and k != 'collection'
        })

    def __del__(self):
        if hasattr(self, '_client'):
            self._client.close()
            del self._client

    @property
    def _collection(self):
        return self._client[self.database][self.collection]

    def size(self) -> int:
        return self._collection.estimated_document_count()

    def store(self, result: Result) -> None:
        self._collection.replace_one({'domain': result.domain}, result_to_json_data(result), True)

    def fetch(self, domain: Domain) -> Optional[Result]:
        result = self._collection.find_one({'domain': domain})
        if result:
            return result_from_json_data(result)

    def contains(self, domain: Domain) -> bool:
        with self._collection.find({'domain': domain}, {}, limit=1) as cursor:
            return bool(next(cursor, 0))

    def delete(self, domain: Domain) -> None:
        self._collection.delete_one({'domain': domain})

    def domains(self) -> Iterable[Domain]:
        with self._collection.find(
                {},
                {
                    '_id': 0,
                    'domain': 1,
                },
        ) as cursor:
            for document in cursor:
                yield document['domain']

    def results(self) -> Iterable[Result]:
        with self._collection.find({}) as cursor:
            yield from map(result_from_json_data, cursor)

    def query(self, query: Query) -> Iterable[Result]:
        and_part = []
        if query.domains:
            domains_in = [d for d in query.domains if not d.startswith('*')]
            domains_re = [{'domain': {'$regex': f'{d[1:]}$'}} for d in query.domains if d.startswith('*')]
            if domains_in and domains_re:
                and_part.append({
                    '$or': [
                        {
                            'domain': {
                                '$in': domains_in,
                            },
                        },
                        *domains_re,
                    ],
                })
            elif domains_in:
                and_part.append({
                    'domain': {
                        '$in': domains_in,
                    },
                })
            else:  # No other choices
                and_part.append({
                    '$or': domains_re,
                })
        if query.types:
            and_part.append({
                'type': {
                    '$in': [str(RRType.from_any(t)) for t in query.types],
                }
            })
        if query.tags:
            and_part.append({
                'tags': {
                    '$regex': str(query.tags)
                }
            })
        search = {'$and': and_part} if and_part else {}
        with self._collection.find(search) as cursor:
            yield from filter(DefaultQuerier.create(query).check_data, map(result_from_json_data, cursor))


__all__ = [
    'MongoDB',
]
