import sqlite3
from sqlite3 import Connection
from typing import Generator

DB_NAME = "wallet.db"


def get_db() -> Generator[Connection, None, None]:
    db = None
    try:
        db = sqlite3.connect(DB_NAME, check_same_thread=False)
        yield db
    finally:
        if db:
            db.close()
