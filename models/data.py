from typing import List
from pydantic import BaseModel


class Annotation(BaseModel):
    post_id: str
    list_topics: List[str]


class Post(BaseModel):
    title: str = "Unknown Title"
    link: str = "Unknown Link"
    media: str = "Unknown Media"
    author: str = "Unknown Author"
    date: str = "Unknown Date"

    def __str__(self) -> str:
        return (
            f"{self.title} - {self.link} - {self.media} - {self.author} - {self.date}"
        )
