from fastapi import APIRouter, Body, Request, BackgroundTasks
from tqdm import tqdm
from models.pub_sub import Message
from utils.funcs import add_data_to_db, get_data_from_db
from models.post import Post
from models.source import Source
from analysis.scraper.extract import ScrapeWebsite
from analysis.bundle.clustering import cluster_by_topic
from routers.llm import compute_analysis
from models.llm import PostQuery

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

    documents = []

    for source_id in tqdm(list_source_ids, desc="Processing sources"):
        source_data = get_data_from_db(source_id)
        source = Source(**source_data["source"])

        article = ScrapeWebsite(source.link)
        if article_content := article.return_article():
            documents.append(article_content)

    print("Clustering sources")
    import pdb; pdb.set_trace()

    cluster_topics, idx_to_topic = cluster_by_topic(
        MODEL_NAME, documents, num_clusters=len(list_source_ids)
    )

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
        )

        post_id = str(post.id)
        cur_documents = [documents[source_idx] for source_idx in list_sources]
        text_content = "\n ".join(cur_documents)

        post_query = PostQuery(text=text_content, post_id=post_id)

        if add_data_to_db(post) != -1:
            compute_analysis(post_query)
