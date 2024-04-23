from typing import List
from analysis.bundle.models.base_model import BaseModel
from collections import defaultdict
from gensim.models.lsimodel import LsiModel
from gensim import corpora


class LSIModel(BaseModel):
    def __init__(self, documents: List[str], num_clusters) -> None:
        self.dictionary = corpora.Dictionary(documents)
        super().__init__(documents, num_clusters)

    def create_vector(self, document: str) -> List[float]:
        return self.dictionary.doc2bow(document)

    def cluster(
        self, num_topics: int = 5
    ) -> tuple[dict[int, List[int]], dict[int, List[str]]]:
        lsi_model = LsiModel(
            self.corpus,
            num_topics=self.num_clusters,
            id2word=self.dictionary,
        )
        cluster_topics = defaultdict(list)

        for i, doc in enumerate(self.documents):
            bow = self.dictionary.doc2bow(doc)
            list_topics = lsi_model[bow]

            topic_idx = max(list_topics, key=lambda x: x[1])[0]
            cluster_topics[topic_idx].append(i)

        idx_to_topic = {
            idx: [token for token, _ in lsi_model.show_topic(idx, topn=num_topics)]
            for idx in range(self.num_clusters)
        }

        return cluster_topics, idx_to_topic
