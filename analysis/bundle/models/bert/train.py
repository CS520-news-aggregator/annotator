from typing import List
from analysis.bundle.models.bert.constants import BERT_MODEL_PATH
from analysis.bundle.models.bert.data.driver import get_data


def create_model(documents: List[str]):
    from bertopic import BERTopic
    from sentence_transformers import SentenceTransformer

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    topic_model = BERTopic(verbose=True, embedding_model=embedding_model)
    topic_model.fit(documents)
    topic_model.save(BERT_MODEL_PATH, save_embedding_model=False)


def create_news_dataset_model():
    list_documents = get_data()
    create_model(list_documents)
