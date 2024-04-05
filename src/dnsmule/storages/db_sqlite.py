from json import loads, dumps
from typing import Optional

from ..api import Storage, Domain, Result, RRType
from ..utils import jsonize


class SQLiteStorage(Storage):
    type = 'sqlite'

    def __init__(self, **config):
        super().__init__()
        self.config = config

    def __enter__(self):
        import sqlite3
        self._client = sqlite3.connect(**self.config)
        self.create_schema()
        return self

    def __exit__(self, *_):
        self._client.close()
        del self._client

    def create_schema(self):
        import sqlite3
        try:
            self._client.execute(
                # language=sqlite
                """
                SELECT 1
                FROM results
                """
            )
        except sqlite3.OperationalError:
            self._client.executescript(
                # language=sqlite
                """
                CREATE TABLE results (
                    name CHAR(255) PRIMARY KEY,
                    data JSON
                );
                """
            )

    def store(self, result: Result):
        self._set(result.name, {
            'types': sorted(RRType.to_text(value) for value in result.types),
            'tags': sorted(result.tags),
            'data': result.data,
        })

    def fetch(self, domain: Domain) -> Optional[Result]:
        json_data = self._get(domain)
        if json_data:
            return Result(
                name=domain,
                types={RRType.from_any(value) for value in json_data['types']},
                tags={*json_data['tags']},
                data=jsonize(json_data['data']),
            )

    def _set(self, key: str, value: dict) -> None:
        with self._client:
            self._client.execute(
                # language=sqlite
                """
                INSERT OR REPLACE INTO results ( name, data ) 
                VALUES (?, ?)
                """,
                (key, dumps(value)),
            )

    def _get(self, key: str) -> Optional[dict]:
        with self._client:
            cursor = self._client.execute(
                # language=sqlite
                """
                SELECT data 
                FROM results
                WHERE name = ?
                """,
                (key,),
            )
            result = cursor.fetchone()
            if result:
                return loads(result[0])
