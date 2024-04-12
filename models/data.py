from typing import List
from pydantic import BaseModel


class Annotation(BaseModel):
    post_id: str
    list_topics: List[str]
