from contextlib import contextmanager
from sqlite3 import Connection, Cursor
from typing import Generator


@contextmanager
def get_connection(path: str) -> Generator[Connection, None, None]:
    connection = Connection(path, check_same_thread=False)
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_cursor(connection: Connection) -> Generator[Cursor, None, None]:
    cursor = connection.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
        connection.commit()
