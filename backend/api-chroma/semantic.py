from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker
import os
import numpy as np

class SemanticEngine:
    def __init__(self, model_name, db):
        print('Created Semantic Engine')
        os.environ["TOKENIZERS_PARALLELISM"] = "true"
        self.model = SentenceTransformer(model_name)
        self.reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
        self.db = db
        self.model.max_seq_length = 512
        
        self.col_titulo = db.get_collection("titulos")
        self.col_desc = db.get_collection("descripciones")
        self.col_headers = db.get_collection("cabeceras_csv")
        self.col_data = db.get_collection("contenido_csv")

    def similarItems(self, query):
        emb = self.model.encode(query, normalize_embeddings=True).tolist()
        res = self.col_titulo.query(query_embeddings=[emb], n_results=4, include=["distances"])
        ids = res['ids'][0][1:] if res['ids'][0] else []
        docs = self.db.getItems(ids)
        for i, hit in enumerate(docs['hits']):
            hit['_score'] = 1 - float(res['distances'][0][i + 1]) if i + 1 < len(res['distances'][0]) else 0.0
        return docs

    def resReranker(self, q, list_results):
        rank_description = []
        final_result = []
        
        for r in list_results:
            desc = str(r.get('description', '')).strip()
            if not desc:
                continue
            rank_description.append([q.strip(), desc])

        if not rank_description:
            return final_result

        scores_normalized = self.reranker.compute_score(rank_description, normalize=True)
        if isinstance(scores_normalized, (float, np.float64)):
            scores_normalized = [scores_normalized]
        
        for index, score in enumerate(scores_normalized):
            if score >= 0.02:
                final_result.append(list_results[index])

        print(f"[RERANKER] Total results after reranking: {len(final_result)}")
        return final_result
        
    def embed(self, text):
        return self.model.encode(text, normalize_embeddings=True)

    # Función para hacer la query a todas las colecciones. Devuelve una lista de resultados con ID y similitud por cada colección
    def query_collections(self, query, k=None):
        emb = self.embed(query)
        collections = self.db.get_all_collections()
        results = {}
        for name, collection in collections.items():
            if name == "datasets": # Skipeo la colección que lleva los datos completos
                continue
            try:
                data = collection.query(
                    query_embeddings=[emb],
                    n_results=k,
                    include=["distances"]
                )
                if not data["ids"] or not data["ids"][0]:
                    results[name] = {
                        "ids": [],
                        "similarities": []
                    }
                    print(f"[QUERY_COLLECTIONS] Collection {name}: No results")
                    continue
    
                similarities = [1 - d for d in data["distances"][0]] if data["distances"][0] else []
    
                results[name] = {
                    "ids": data["ids"][0],
                    "similarities": similarities
                }
    
            except Exception as e:
                print(f"[QUERY_COLLECTIONS] Error querying collection {name}: {e}")
                results[name] = {
                    "ids": [],
                    "similarities": []
                }
    
        return (
            results.get("titulos", {"ids": [], "similarities": []}),
            results.get("descripciones", {"ids": [], "similarities": []}),
            results.get("cabeceras_csv", {"ids": [], "similarities": []}),
            results.get("contenido_csv", {"ids": [], "similarities": []})
        )
