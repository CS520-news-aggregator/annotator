from typing import List

from bertopic import BERTopic
from analysis.bundle.models.base_model import BaseModel
from analysis.bundle.models.bert.constants import BERT_MODEL_PATH
from sentence_transformers import SentenceTransformer


# TODO - complete
class BERTModel(BaseModel):
    def __init__(self, documents: List[str], num_clusters) -> None:
        super().__init__(documents, num_clusters)

        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.bert_model: BERTopic = BERTopic.load(
            BERT_MODEL_PATH, embedding_model=embedding_model
        )

    def create_vector(self, document: str) -> List[float]:
        # Do not need vector for BERTopic
        return super().create_vector(document)

    def cluster(self) -> tuple[dict[int, List[int]], dict[int, List[str]]]:
        topics, probs = self.bert_model.fit(self.documents)
        print(f"Topics: {topics}")
        print(f"Probabilities: {probs}")
        raise NotImplementedError("cluster method is not completely implemented")
