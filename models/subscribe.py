from pydantic import BaseModel


class Message(BaseModel):
    post_id: str
    message: str
