
# Re-import necessary libraries and reload the file
import pandas as pd
import json
import yaml
import sys
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def cluster(file_path, output_file, model_output_file, n_clusters):
    # Load the new file
    data = pd.read_csv(file_path)

    def extract_items_with_index(row):
        try:
            items = json.loads(row)['items']
            return [{'description': item['description'], 'index': item['item']} for item in items]
        except (KeyError, TypeError, json.JSONDecodeError):
            return []

    data['item_details'] = data['items'].apply(extract_items_with_index)

    flat_items = data.explode('item_details')
    flat_items = flat_items.dropna(subset=['item_details']).reset_index(drop=True)

    flat_items['item_descriptions'] = flat_items['item_details'].apply(lambda x: x['description'])
    flat_items['item_index'] = flat_items['item_details'].apply(lambda x: x['index'])

    flat_items_data = flat_items[['tender_id', 'category', 'item_index', 'item_descriptions']]

    spanish_stop_words = [
        'que', 'de', 'el', 'la', 'los', 'las', 'un', 'una', 'y', 'en', 'para', 'por', 
        'con', 'del', 'al', 'se', 'lo', 'como', 'más', 'sin', 'su', 'a', 'es', 'o', 'sus'
    ]
    vectorizer = TfidfVectorizer(max_features=500, stop_words=spanish_stop_words)
    item_embeddings = vectorizer.fit_transform(flat_items_data['item_descriptions'])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    flat_items_data['cluster'] = kmeans.fit_predict(item_embeddings.toarray())

    flat_items_data.to_csv(output_file, index=False)
    # save model as .pkl
    joblib.dump(kmeans, model_output_file)

if __name__ == '__main__':
    with open("params.yaml") as file:
        params = yaml.safe_load(file)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    model_output_file = sys.argv[3]
    cluster(input_file, output_file, model_output_file, params['n_clusters'])