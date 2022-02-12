from sqlite3 import Connection
from typing import Optional

from app.core.models.user import User
from app.core.repositories import IUserRepository
from app.core.security.api_key_generator import ApiKey
from app.infra.repositories.sqlite.utils import get_cursor


class SQLiteUserRepository(IUserRepository):
    connection: Connection

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "create table if not exists user("
                "user_id integer primary key autoincrement,"
                "api_key text unique not null);"
            )

    def add_user(self, api_key: ApiKey) -> None:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "insert into user(api_key) values(:api_key);",
                {"api_key": api_key.api_key},
            )

    def find(self, api_key: ApiKey) -> Optional[User]:
        with get_cursor(self.connection) as cursor:
            cursor.execute(
                "select user_id, api_key from user where api_key=:api_key;",
                {"api_key": api_key.api_key},
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return User(id=row[0], api_key=row[1])
