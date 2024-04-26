from typing import List
from fastapi import APIRouter, Body, Request, BackgroundTasks
from tqdm import tqdm
from models.pub_sub import Message
from utils.funcs import add_data_to_db, get_data_from_db
from models.post import Post
from models.source import Source
from models.recommendation import Recommendation, PostRecommendation
from analysis.scraper.extract import ScrapeWebsite
from analysis.bundle.clustering import cluster_by_topic
from routers.llm import compute_analysis
from analysis.llm.ollama.calls import ollama_keep_alive
from models.llm import PostQuery
from analysis.user.preferences import get_all_user_recommendations
from datetime import datetime

subscriber_router = APIRouter(prefix="/subscriber")
MODEL_NAME = "bert"


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

    documents: List[str] = []
    sources: List[Source] = []

    for source_id in tqdm(list_source_ids, desc="Processing sources"):
        source_data = get_data_from_db(
            "aggregator/get-aggregation", {"source_id": source_id}
        )

        source = Source(**source_data["source"])
        sources.append(source)

        article = ScrapeWebsite(source.link)
        if article_content := article.return_article():
            documents.append(article_content)

    print("Clustering sources")

    cluster_topics, idx_to_topic = cluster_by_topic(
        MODEL_NAME, documents, num_clusters=len(list_source_ids)
    )

    ollama_keep_alive(-1)
    list_posts: List[Post] = []

    for cluster_idx, list_sources in tqdm(
        cluster_topics.items(),
        desc="Generating summaries and titles",
    ):
        cluster_source_ids = []

        for source_idx in list_sources:
            source_id = list_source_ids[source_idx]
            cluster_source_ids.append(source_id)

        post = Post(
            source_ids=cluster_source_ids,
            topics=idx_to_topic[cluster_idx],
            date=sources[0].date,  # FIXME: for now, put the date of the first source
        )

        post_id = str(post.id)
        cur_documents = [documents[source_idx] for source_idx in list_sources]
        text_content = "\n ".join(cur_documents)

        post_query = PostQuery(text=text_content, post_id=post_id)

        if add_data_to_db("annotator/add-post", post) == -1:
            compute_analysis(post_query)
            list_posts.append(post)

    ollama_keep_alive(0)

    # FIXME: user posts empty for new users upon registration
    user_recommendations = get_all_user_recommendations(list_posts)

    for user_id, user_recomm_posts in tqdm(
        user_recommendations, desc="Adding user recommendations"
    ):
        post_recommendations = [
            PostRecommendation(post_id=post.id, date=post.date or get_cur_date())
            for post in user_recomm_posts
        ]

        user_recommendation = Recommendation(
            user_id=user_id, post_recommendations=post_recommendations
        )

        add_data_to_db("recommendation/add-recommendation", user_recommendation)


def get_cur_date():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
