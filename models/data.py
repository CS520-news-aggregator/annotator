from typing import List
from pydantic import BaseModel


class Post(BaseModel):
    source_ids: List[str]
    topics: List[str]


class Source(BaseModel):
    title: str = "Unknown Title"
    link: str = "Unknown Link"
    media: str = "Unknown Media"
    author: str = "Unknown Author"
    date: str = "Unknown Date"

    def __str__(self) -> str:
        return (
            f"{self.title} - {self.link} - {self.media} - {self.author} - {self.date}"
        )
