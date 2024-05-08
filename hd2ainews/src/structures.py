from dataclasses import dataclass
from datetime import datetime


class News:
    id: str
    published: int
    type: int
    message: str
    tagIds: list[str]

    def __init__(
        self, id: str, published: int, type: int, message: str, tagIds: list[str]
    ):
        from hd2ainews.src.hd2 import API

        self.id = id
        self.published = API.fix_timestamp(published)
        self.type = type
        self.message = message
        self.tagIds = tagIds

    def __str__(self) -> str:
        return f"{datetime.fromtimestamp(self.published).strftime('%Y-%m-%d %H:%M:%S')}: {self.message}"
