from sentence_transformers import SentenceTransformer
from db import dbEngine
from FlagEmbedding import FlagReranker
import os
import numpy as np
import chromadb

class SemanticEngine:
    def __init__(self, model_name):
        print('Created Semantic Engine')
        os.environ["TOKENIZERS_PARALLELISM"] = "true"

        self.model = SentenceTransformer(model_name)
        self.reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
        self.db = dbEngine()
        self.model.max_seq_length = 512

        # Cliente y colecciones Chroma
        client = chromadb.PersistentClient(path="./chroma_data")
        
        self.col_titulo = client.get_or_create_collection(name="titulos")
        self.col_desc = client.get_or_create_collection(name="descripciones")
        self.col_headers = client.get_or_create_collection(name="cabeceras_csv")
        self.col_data = client.get_or_create_collection(name="contenido_csv")

    def similarItems(self, query):
        emb = self.model.encode(query).tolist()
        res = self.col_titulo.query(query_embeddings=[emb], n_results=4)

        ids = res['ids'][0][1:]  # Excluir el más similar (primer resultado)
        docs = self.db.getItems(ids)

        # Agregar similitud al resultado (si es necesario)
        for i, hit in enumerate(docs['hits']):
            hit['_score'] = float(res['distances'][0][i + 1])  # desde el segundo
        return docs

    def resReranker(self, q, list_results):
        rank_description = []
        final_result = []
    
        print(f"[DEBUG] Ejecutando reranker para consulta: '{q}'")
        print(f"[DEBUG] Número de resultados a evaluar: {len(list_results)}")

        if len(list_results) > 1:
            for r in list_results:
                desc = r.get('description', '')
                print(f"[DEBUG] → Evaluando ID: {r.get('id')} | Descripción: {desc}")
                rank_description.append([q, desc])
        
            scores_description = self.reranker.compute_score(rank_description, normalize=True)
        
            if isinstance(scores_description, float) or isinstance(scores_description, np.float64):
                scores_description = [scores_description]
        
            for index, score in enumerate(scores_description):
                r_id = list_results[index].get('id')
                print(f"[DEBUG] Score para ID {r_id}: {score:.5f}")
                #if score >= 0.02:
                print(f"[DEBUG] → ACEPTADO (>= 0.02): {r_id}")
                final_result.append(list_results[index])
                #else:
                    #print(f"[DEBUG] → DESCARTADO (< 0.02): {r_id}")
        
        print(f"[DEBUG] Total aceptados tras reranker: {len(final_result)}")
        return final_result

    def embed(self, text):
        return self.model.encode(text).tolist()

    def query_collections(self, query, k=50):
        emb = self.embed(query)
        r1 = self.col_titulo.query(query_embeddings=[emb], n_results=k)
        r2 = self.col_desc.query(query_embeddings=[emb], n_results=k)
        r3 = self.col_headers.query(query_embeddings=[emb], n_results=k)
        r4 = self.col_data.query(query_embeddings=[emb], n_results=k)

        return r1, r2, r3, r4
