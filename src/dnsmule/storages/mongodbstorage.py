import re
from typing import Iterable, Optional

from .abstract import Storage, result_from_json_data, result_to_json_data, Query, BasicSearch, WildcardCollection
from .. import Result, Domain, RRType


def to_mongo_condition(key: str, collection: WildcardCollection) -> dict:
    conditions = [
        {
            key: {
                '$in': [*collection.exact],
            }
        }
    ]
    if collection.prefix:
        for prefix in collection.prefix:
            conditions.append({
                key: {
                    '$regex': f'^{re.escape(prefix)}',
                }
            })
    if collection.suffix:
        for suffix in collection.suffix:
            conditions.append({
                key: {
                    '$regex': f'{re.escape(suffix)}$',
                }
            })
    if collection.search:
        for search in collection.search:
            conditions.append({
                key: {
                    '$regex': search.pattern
                }
            })
    return conditions[0] if len(conditions) == 1 else {'$or': conditions}


def mongo_and(*conditions: dict) -> dict:
    if len(conditions) == 1:
        return conditions[0]
    elif len(conditions) == 0:
        return {}
    else:
        return {
            '$and': conditions,
        }


class MongoStorage(Storage):
    database: str = 'dnsmule'
    collection: str = 'results'

    def __init__(self, **kwargs):
        super(MongoStorage, self).__init__(**kwargs)
        import pymongo
        driver_kwargs = self._kwargs
        driver_kwargs.pop('database', None)
        driver_kwargs.pop('collection', None)
        self._client = pymongo.MongoClient(**driver_kwargs)
        self._collection.create_index(
            [('domain', pymongo.DESCENDING)],
            name='idx_domain_u',
            background=True,
            unique=True,
        )

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
        conditions = []
        bs = BasicSearch(query)
        if bs.domains:
            conditions.append(to_mongo_condition('domain', bs.domains))
        if bs.types:
            conditions.append({
                'type': {
                    '$in': [str(RRType.from_any(t)) for t in bs.types],
                }
            })
        if bs.tags:
            conditions.append(to_mongo_condition('tags', bs.tags))
        if bs.data:
            for key in bs.data:
                conditions.append({
                    f'data.{key}': {
                        '$exists': True,
                    }
                })
        with self._collection.find(mongo_and(*conditions)) as cursor:
            yield from map(result_from_json_data, cursor)


__all__ = [
    'MongoStorage',
]
