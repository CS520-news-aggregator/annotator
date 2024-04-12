from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routers.subscriber import subscriber_router
from utils import subscribe_to_publisher
import os


origins = ["*"]
app = FastAPI(title="News Annotator", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subscriber_router)


@app.get("/")
async def root():
    return {"Hello": "World"}


if __name__ == "__main__":
    subscribe_to_publisher(
        os.getenv("SUBSCRIBER_IP", "localhost"),
        8020,
        os.getenv("PUBLISHER_IP", "localhost"),
        8010,
    )
    uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True, workers=1)
