from json import dumps, loads
from typing import Optional

from .key_value import AbstractKVStorage


class MySQLStorage(AbstractKVStorage):
    type = 'mysql'

    def __init__(self, **config):
        super().__init__()
        self.config = config

    def __enter__(self):
        import pymysql
        self._client = pymysql.connect(**self.config)
        self.create_schema()
        return self

    def __exit__(self, *_):
        self._client.close()
        del self._client

    def create_schema(self):
        import pymysql
        c = self._client.cursor()
        try:
            c.execute(
                # language=mysql
                """
                SELECT 1
                FROM results
                """
            )
        except pymysql.err.ProgrammingError:
            c.execute(
                # language=mysql
                """
                CREATE TABLE results
                (
                    name CHAR(253) NOT NULL,
                    data JSON,
                    PRIMARY KEY (name)
                );
                """
            )
        finally:
            c.close()

    def _set(self, key: str, value: dict) -> None:
        c = self._client.cursor()
        try:
            c.execute(
                # language=mysql
                """
                INSERT INTO results ( name, data ) 
                VALUES (%(name)s, %(data)s)
                ON DUPLICATE KEY UPDATE data = VALUES(data)
                """,
                {
                    'name': key,
                    'data': dumps(value),
                },
            )
        finally:
            c.close()

    def _get(self, key: str) -> Optional[dict]:
        c = self._client.cursor()
        try:
            c.execute(
                # language=mysql
                """
                SELECT data 
                FROM results
                WHERE name = %(name)s
                """,
                {
                    'name': key,
                },
            )
            result = c.fetchone()
            if result:
                return loads(result[0])
        finally:
            c.close()
