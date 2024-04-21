from collections import defaultdict
from gensim.models.ldamodel import LdaModel
from gensim import corpora
from analysis.bundle.preprocess import preprocess

# TODO - Use BERTopic for clustering
# from bertopic import BERTopic

def cluster_by_topic(documents, num_clusters, num_topics):
    processed_docs = [preprocess(doc) for doc in documents]

    dictionary = corpora.Dictionary(processed_docs)
    corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

    lda_model = LdaModel(corpus, num_topics=num_clusters, id2word=dictionary, passes=15)
    cluster_topics = defaultdict(list)

    for i, doc in enumerate(processed_docs):
        bow = dictionary.doc2bow(doc)
        list_topics = lda_model.get_document_topics(bow)

        topic_idx = max(list_topics, key=lambda x: x[1])[0]
        cluster_topics[topic_idx].append(i)

    idx_to_topic = {
        idx: [token for token, _ in lda_model.show_topic(idx, topn=num_topics)]
        for idx in range(num_clusters)
    }
    return cluster_topics, idx_to_topic
