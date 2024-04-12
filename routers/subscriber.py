from fastapi import APIRouter, Body, Request
from models.subscribe import Message
from utils import add_data_to_db
from models.data import Annotation

subscriber_router = APIRouter(prefix="/subscriber")


@subscriber_router.post("/update")
async def update_from_publisher(_: Request, message: Message = Body(...)):
    print(f"Received message: {message}")
    annotation = Annotation(
        post_id=message.post_id,
        list_topics=["topic1", "topic2", "topic3"],
    )
    annotation_id = add_data_to_db(annotation)
    print(f"Added annotation with ID: {annotation_id}")
    return {"message": "Added annotation", "annotation_id": annotation_id}
