from fastapi import APIRouter, Body, Request, BackgroundTasks
from tqdm import tqdm
from models.subscribe import Message
from utils.funcs import add_data_to_db, get_data_from_db
from models.data import Annotation, Post
from analysis.scraper.extract import ScrapeWebsite
from analysis.bundle.clustering import cluster_by_topic

subscriber_router = APIRouter(prefix="/subscriber")


@subscriber_router.post("/update")
async def update_from_publisher(
    _: Request, background_tasks: BackgroundTasks, message: Message = Body(...)
):
    print(f"Received message: {message}")
    add_background_task(background_tasks, message.post_ids)
    return {"message": "Annotations in progress"}


def add_background_task(background_tasks: BackgroundTasks, list_post_ids: list[str]):
    background_tasks.add_task(process_posts, list_post_ids)


def process_posts(list_post_ids: list[str]):
    if not list_post_ids:
        print("No posts to process")
        return

    documents = []

    for post_id in tqdm(list_post_ids, desc="Processing posts"):
        post_data = get_data_from_db(post_id)
        post = Post(**post_data["post"])

        article = ScrapeWebsite(post.link)
        documents.append(article.return_article())

    cluster_topics, idx_to_topic = cluster_by_topic(
        documents, num_clusters=len(list_post_ids), num_topics=5
    )

    for cluster_idx, list_posts in cluster_topics.items():
        cluster_post_ids = []

        for post_idx in list_posts:
            post_id = list_post_ids[post_idx]
            cluster_post_ids.append(post_id)

        annotation = Annotation(
            post_ids=cluster_post_ids,
            topics=idx_to_topic[cluster_idx],
        )
        add_data_to_db(annotation)
