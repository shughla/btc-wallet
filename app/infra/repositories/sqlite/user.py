from sqlite3 import Connection, IntegrityError
from typing import Optional

from app.core.exceptions import DuplicateUserApiKeyException
from app.core.models.user import User
from app.core.repositories import IUserRepository
from app.core.security.api_key_generator import ApiKey


class SQLiteUserRepository(IUserRepository):
    connection: Connection

    def __init__(self, connection: Connection) -> None:
        self.connection = connection
        cursor = self.connection.cursor()
        cursor.execute(
            "create table if not exists user("
            "user_id integer primary key autoincrement,"
            "api_key text unique not null);"
        )
        cursor.close()

    def add_user(self, api_key: ApiKey) -> None:
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                "insert into user(api_key) values(:api_key);",
                {"api_key": api_key.api_key},
            )
            cursor.close()
        except IntegrityError:
            raise DuplicateUserApiKeyException()

    def find(self, api_key: ApiKey) -> Optional[User]:
        cursor = self.connection.cursor()
        cursor.execute(
            "select user_id, api_key from user where api_key=:api_key;",
            {"api_key": api_key.api_key},
        )
        row = cursor.fetchone()
        print(row)
        cursor.close()
        if row is None:
            return None
        return User(id=row[0], api_key=row[1])
