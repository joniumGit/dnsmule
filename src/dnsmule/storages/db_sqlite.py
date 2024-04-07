from json import loads, dumps
from typing import Optional

from .key_value import AbstractKVStorage


class SQLiteStorage(AbstractKVStorage):
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
