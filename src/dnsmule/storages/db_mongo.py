from typing import Optional

from ..api import Storage, Domain, Result, RRType
from ..utils import jsonize


class MongoStorage(Storage):
    type = 'mongodb'

    database: str
    collection: str

    config: dict

    def __init__(
            self,
            *,
            database: str = 'dnsmule',
            collection: str = 'results',
            **config,
    ):
        super().__init__()
        self.database = database
        self.collection = collection
        self.config = config

    def __enter__(self):
        import pymongo
        self._client = pymongo.MongoClient(**self.config)
        self._collection.create_index(
            [('domain', pymongo.DESCENDING)],
            name='idx_domain_u',
            background=True,
            unique=True,
        )
        return self

    def __exit__(self, *_):
        self._client.close()
        del self._client

    @property
    def _collection(self):
        return self._client[self.database][self.collection]

    def store(self, result: Result) -> None:
        self._collection.replace_one(
            {'domain': result.name},
            {
                'domain': result.name,
                'types': sorted(RRType.to_text(value) for value in result.types),
                'tags': sorted(result.tags),
                'data': jsonize(result.data),
            },
            True,
        )

    def fetch(self, domain: Domain) -> Optional[Result]:
        json_data = self._collection.find_one({'domain': domain})
        if json_data:
            return Result(
                name=domain,
                types={RRType.from_any(value) for value in json_data['types']},
                tags={*json_data['tags']},
                data=json_data['data'],
            )


__all__ = [
    'MongoStorage',
]
