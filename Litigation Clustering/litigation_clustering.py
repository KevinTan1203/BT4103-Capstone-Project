import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from textblob import TextBlob
import joblib

embedder = SentenceTransformer('all-mpnet-base-v2')


def text_cleaning(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z]', ' ', text)
    text = re.sub(r' +', ' ', text)
    text = str(TextBlob(text).correct())
    return text


def generate_model(df, clusters):
    corpus = list(df.iloc[:, 0].apply(text_cleaning))
    corpus_embeddings = embedder.encode(corpus)
    
    clustering_model = KMeans(n_clusters=clusters, n_init='auto', random_state=10)
    clustering_model.fit(corpus_embeddings)
    
    return clustering_model


def generate_litigation_main_cause_model():
    df = pd.read_csv('./Dataset/litigation_data/litigation_main_cause.csv', dtype=str).dropna()
    clustering_model = generate_model(df, 5)
    joblib.dump(clustering_model, 'litigation_main_cause_clustering.pkl')
    
    
def generate_litigation_case_status_model():
    df = pd.read_csv('./Dataset/litigation_data/litigation_case_status.csv', dtype=str).dropna()
    clustering_model = generate_model(df, 8)
    joblib.dump(clustering_model, 'litigation_case_status_clustering.pkl')
    
    
def generate_litigation_party_status_model():
    df = pd.read_csv('./Dataset/litigation_data/litigation_party_status.csv', dtype=str).dropna()
    clustering_model = generate_model(df, 8)
    joblib.dump(clustering_model, 'litigation_party_status_clustering.pkl')
    
    
def label_litigation_main_cause(clustering_model, text):
    categories = {
        0: 'Contracts', 
        1: 'Negligence & Accidents', 
        2: 'Others', 
        3: 'Provision of Goods and Services', 
        4: 'Financials', 
    }
    text_label = clustering_model.predict(embedder.encode([str(text)]))[0]
    return categories[text_label]


def label_litigation_case_status(clustering_model, text):
    categories = {
        0: 'Discharged', 
        1: 'Concluded', 
        2: 'Bankruptcy Related', 
        3: 'Concluded', 
        4: 'Others', 
        5: 'Concluded', 
        6: 'Discharged', 
        7: 'Others', 
    }
    text_label = clustering_model.predict(embedder.encode([str(text)]))[0]
    return categories[text_label]


def label_litigation_party_status(clustering_model, text):
    categories = {
        0: 'Others', 
        1: 'Bankruptcy Related', 
        2: 'Judgement', 
        3: 'Discharge Notice', 
        4: 'Others', 
        5: 'Others', 
        6: 'Annulment', 
        7: 'Judgement', 
    }
    text_label = clustering_model.predict(embedder.encode([str(text)]))[0]
    return categories[text_label]