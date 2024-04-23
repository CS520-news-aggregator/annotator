from typing import List
from pydantic import BaseModel


class Message(BaseModel):
    post_ids: List[str]
    message: str
