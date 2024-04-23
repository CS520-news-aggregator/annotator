from fastapi import APIRouter, Body, Request, BackgroundTasks
from tqdm import tqdm
from models.subscribe import Message
from utils.funcs import add_data_to_db, get_data_from_db
from models.data import Post, Source
from analysis.scraper.extract import ScrapeWebsite
from analysis.bundle.clustering import cluster_by_topic

subscriber_router = APIRouter(prefix="/subscriber")
MODEL_NAME = "lda"


@subscriber_router.post("/update")
async def update_from_publisher(
    _: Request, background_tasks: BackgroundTasks, message: Message = Body(...)
):
    print(f"Received message: {message}")
    add_background_task(background_tasks, message.source_ids)
    return {"message": "Annotations in progress"}


def add_background_task(background_tasks: BackgroundTasks, list_source_ids: list[str]):
    background_tasks.add_task(process_sources, list_source_ids)


def process_sources(list_source_ids: list[str]):
    if not list_source_ids:
        print("No sources to process")
        return

    documents = []

    for source_id in tqdm(list_source_ids, desc="Processing sources"):
        source_data = get_data_from_db(source_id)
        source = Source(**source_data["source"])

        article = ScrapeWebsite(source.link)
        if article_content := article.return_article():
            documents.append(article_content)

    cluster_topics, idx_to_topic = cluster_by_topic(
        MODEL_NAME, documents, num_clusters=len(list_source_ids)
    )

    for cluster_idx, list_sources in cluster_topics.items():
        cluster_source_ids = []

        for source_idx in list_sources:
            source_id = list_source_ids[source_idx]
            cluster_source_ids.append(source_id)

        post = Post(
            source_ids=cluster_source_ids,
            topics=idx_to_topic[cluster_idx],
        )
        add_data_to_db(post)
