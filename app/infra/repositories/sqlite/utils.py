import sqlite3
from contextlib import contextmanager
from sqlite3 import Connection, Cursor
from typing import Generator

from app.core.const import Config


def get_connection(path: str = Config.DATABASE_NAME) -> Connection:
    return sqlite3.connect(path, check_same_thread=False)


@contextmanager
def get_cursor(connection: Connection) -> Generator[Cursor, None, None]:
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        connection.commit()
