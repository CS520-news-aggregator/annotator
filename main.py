from contextlib import asynccontextmanager
import os
import sys
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from analysis.llm.ollama.calls import add_model_to_ollama
from routers.subscriber import subscriber_router
from routers.llm import llm_router
from utils.funcs import subscribe_to_publisher


@asynccontextmanager
async def lifespan(_: FastAPI):
    subscribe_to_publisher(
        os.getenv("SUBSCRIBER_IP", "localhost"),
        8020,
        os.getenv("PUBLISHER_IP", "localhost"),
        8010,
    )
    add_model_to_ollama()
    yield


origins = ["*"]
app = FastAPI(title="News Annotator", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subscriber_router)
app.include_router(llm_router)


@app.get("/")
async def root():
    return {"Hello": "World"}


def train_bert():
    from analysis.bundle.models.bert.data.social_animal_driver import (
        get_social_news_data,
    )
    from analysis.bundle.models.bert.train import create_model, save_model, load_model
    from analysis.bundle.models.bert.constants import FILE_DIR
    from bertopic import BERTopic

    prev_topic_model = load_model(
        os.path.join(os.path.join(FILE_DIR, "saved_models"), "bert_model_all_news.bin")
    )

    list_documents = get_social_news_data()
    cur_topic_model = create_model(list_documents)

    topic_model = BERTopic.merge_models([prev_topic_model, cur_topic_model])
    save_model(topic_model)


def debug():
    from analysis.bundle.clustering import cluster_by_topic
    from analysis.scraper.extract import ScrapeWebsite
    from routers.llm import compute_analysis
    from models.llm import PostQuery

    list_links = [
        "https://www.cnn.com/2024/04/20/politics/mike-johnson-ukraine-aid-russia-zelensky-putin/index.html",
        "https://www.foxnews.com/politics/nothing-more-backwards-than-us-funding-ukraine-border-security-but-not-our-own-conservatives-say",
        "https://www.bbc.com/news/world-us-canada-68848277",
        "https://www.cnn.com/2024/04/20/weather/dubai-flood-rain-life-halts-weather-intl/index.html",
        "https://www.bbc.com/news/world-middle-east-68864207",
        "https://www.bbc.com/news/entertainment-arts-68863614",
        "https://www.cnn.com/2024/04/19/opinions/mother-daughter-taylor-swift-experience-the-tortured-poets-department-bass/index.html",
    ]

    list_documents = [ScrapeWebsite(link).return_article() for link in list_links]
    list_documents = [doc for doc in list_documents if doc]

    compute_analysis(PostQuery(post_id="1", text=list_documents[0]))

    cluster_topics, idx_to_topic = cluster_by_topic(
        "bert", list_documents, num_clusters=len(list_links)
    )

    print(cluster_topics)
    print(idx_to_topic)

    # from analysis.bundle.models.bert.train import create_news_dataset_model

    # create_news_dataset_model()

    # add_model_to_ollama()
    # from analysis.llm.ollama.calls import (
    #     generate_text_from_ollama,
    #     parse_ollama_response,
    # )

    # response_json = generate_text_from_ollama("The world is")
    # response = parse_ollama_response(response_json)
    # print(response)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        debug()
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True, workers=1)
