from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    api_key: str
