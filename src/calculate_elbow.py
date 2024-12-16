import pandas as pd
import json
import matplotlib.pyplot as plt
import sys
import yaml
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def extract_items(row):
    try:
        items = json.loads(row)['items']
        return [item['description'] for item in items]
    except (KeyError, TypeError, json.JSONDecodeError):
        return []

def calculate_elbow(file_path, output_file, max_clusters):
    data = pd.read_csv(file_path)
    data['item_descriptions'] = data['items'].apply(extract_items)
    items_data = data.explode('item_descriptions')[['tender_id', 'category', 'item_descriptions']]
    items_data = items_data.dropna(subset=['item_descriptions']).reset_index(drop=True)


    spanish_stop_words = list(ENGLISH_STOP_WORDS) + [
        'que', 'de', 'el', 'la', 'los', 'las', 'un', 'una', 'y', 'en', 'para', 'por', 
        'con', 'del', 'al', 'se', 'lo', 'como', 'más', 'sin', 'su', 'a', 'es', 'o', 'sus'
    ]

    vectorizer = TfidfVectorizer(max_features=500, stop_words=spanish_stop_words)
    item_embeddings = vectorizer.fit_transform(items_data['item_descriptions'])

    item_embeddings_dense = item_embeddings.toarray()

    inertia = []
    cluster_range = range(2, max_clusters)  

    for k in cluster_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(item_embeddings_dense)
        inertia.append(kmeans.inertia_)

    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, inertia, marker='o')
    plt.title('Elbow Method for Optimal Clusters')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Inertia')
    plt.grid()
    plt.savefig(output_file)

if __name__ == '__main__':
    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    calculate_elbow(input_file, output_file, params['elbow_max_clusters'])