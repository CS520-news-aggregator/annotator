from typing import List
from analysis.bundle.preprocess import preprocess
from analysis.bundle.models.base_model import BaseModel
from analysis.bundle.models.lda import LDAModel
from analysis.bundle.models.lsi import LSIModel
from analysis.bundle.models.bert.bert_topic import BERTModel

# TODO - Use BERTopic for clustering
# from bertopic import BERTopic

get_class = lambda x: globals()[x]


def cluster_by_topic(model_name: str, documents: List[str], num_clusters: int):
    processed_docs = [preprocess(doc) for doc in documents] if model_name != 'bert' else documents
    model: BaseModel = get_class(f"{model_name.upper()}Model")(
        processed_docs, num_clusters
    )
    return model.cluster()
