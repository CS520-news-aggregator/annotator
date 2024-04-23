import re
import spacy
import nltk
from nltk.corpus import stopwords

nlp = spacy.load("en_core_web_lg")


def remove_stopwords(doc):
    words = doc.split()
    words = [word for word in words if word not in stopwords.words("english")]
    return " ".join(words)


def remove_punctuation(doc):
    remove_punc = re.compile(r"[^A-Za-z ]")
    return re.sub(remove_punc, "", doc)


def preprocess(doc):
    doc = remove_punctuation(doc)
    doc = remove_stopwords(doc)
    doc = nlp(doc)
    doc = [token.text for token in doc.ents if token.label_ != "CARDINAL"]
    return doc
