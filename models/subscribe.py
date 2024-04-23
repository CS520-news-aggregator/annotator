from typing import List
from pydantic import BaseModel


class Message(BaseModel):
    source_ids: List[str]
    message: str
