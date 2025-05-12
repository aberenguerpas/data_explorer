import pickle
import numpy as np
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

class SearchEngine:
    def __init__(self, db, generative, semantic):
        print('Created Search Engine')
        self.db = db
        self.generative = generative
        self.semantic = semantic

        self.pesos = {
            "title": 0.5,
            "description": 0.3,
            "header": 0.1,
            "rows": 0.1
        }
        self.umbral_similitud = 0.6
        self.top_n = 10
        self.k = 50

    def search(self, text):
        print(f"[SEARCH] Consulta recibida: {text}")
        query_type = self.generative.classify_query_type(text)
        
        print(f"[SEARCH] Tipo de consulta clasificada: {'intent' if query_type == 1 else 'keyword'}")
        if query_type == 1:
            keywords = self.generative.getKeywords(text)
            print(f"[SEARCH] Keywords generadas: {keywords}")
            return self.get_intent_results(keywords, text)
        else:
            return self.get_keyword_results(text)

    def get_intent_results(self, queries, intent):
        print(f"[INTENT] Ejecutando búsqueda para la intención: '{intent}'")
        
        resultados_finales = []
        total_hits = 0
        ya_encontrados = set()
    
        # Iterar por cada keyword generada y procesar cada una por separado
        for q in queries['keywords']:
            query = q['consulta']
            print(f"[INTENT] Ejecutando consulta para la keyword: '{query}'")
    
            # Generar embedding de la keyword
            emb_q = self.semantic.model.encode([query])[0]  # shape (dim,)
    
                # Recuperar candidatos de cada colección para esta keyword
            r1 = self.semantic.col_titulo.query(query_embeddings=[emb_q], n_results=self.k)
            r2 = self.semantic.col_desc.query(query_embeddings=[emb_q], n_results=self.k)
            r3 = self.semantic.col_headers.query(query_embeddings=[emb_q], n_results=self.k)
            r4 = self.semantic.col_data.query(query_embeddings=[emb_q], n_results=self.k)
    
            def get_score_dict(r):
                return {r['ids'][0][i]: r['distances'][0][i] for i in range(len(r['ids'][0]))}
    
            # Obtener puntuaciones de cada colección
            scores1 = get_score_dict(r1)
            scores2 = get_score_dict(r2)
            scores3 = get_score_dict(r3)
            scores4 = get_score_dict(r4)
    
            # Unir los IDs de todas las colecciones
            all_ids = set(scores1.keys()) | set(scores2.keys()) | set(scores3.keys()) | set(scores4.keys())
            
            # Combinar las puntuaciones de las colecciones con ponderación
            combined_scores = {}
            for _id in all_ids:
                score = (
                    scores1.get(_id, 0) * 0.5 +
                    scores2.get(_id, 0) * 0.3 +
                    scores3.get(_id, 0) * 0.1 +
                    scores4.get(_id, 0) * 0.1
                )
    
                # Filtrar si la puntuación es mayor al umbral de similitud
                if score > 0.8:
                    combined_scores[_id] = score
    
            # Ordenar los resultados por puntuación
            ids_ordenados = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            ids_finales = [id for id, _ in ids_ordenados]
            print(f"[INTENT] IDs seleccionados para '{query}' (score > 0.8): {ids_finales}")
    
            # Recuperar metadatos de los top resultados
            resultados = self.db.getItems(ids_finales)
            hits = resultados.get('hits', [])
    
            for hit in hits:
                dataset_id = hit['id']
                score = combined_scores.get(dataset_id, None)
                title = hit.get('title', 'SIN TÍTULO')
                description = hit.get('description', 'SIN DESCRIPCIÓN')
    
            # Aplicar reranking a los hits recuperados
            reranked_hits = self.semantic.resReranker(query, hits)
            print(f"[INTENT] Resultados tras rerank para '{query}': {[r.get('id') for r in reranked_hits]}")
    
            # Filtrar resultados ya encontrados
            reranked_hits = [r for r in reranked_hits if r['id'] not in ya_encontrados]
            if reranked_hits:
                for r in reranked_hits:
                    ya_encontrados.add(r['id'])
                q['resultados'] = {'hits': reranked_hits}
                total_hits += len(reranked_hits)
                resultados_finales.append(q)
    
        print(f"[INTENT] Total resultados acumulados: {total_hits}")
        
        if total_hits == 0:
            return {
                "type": "intent",
                "total": 0,
                "hits": 0,
                "intro": self.generative.generateNoResultsResponse(intent),
                "additional": ''
            }

        return {
            "type": "intent",
            "total": total_hits,
            "hits": resultados_finales,
            "intro": queries.get('intro', ''),
            "additional": queries.get('extra', '')
        }
    
    def get_keyword_results(self, query: str):
        print(f"[KEYWORD] Ejecutando búsqueda manual para: '{query}'")

        # 1) Generar embedding bruto de la query
        emb_q = self.semantic.model.encode([query])[0]  # shape (dim,)

        # 2) Recuperar candidatos por aproximación (solo para acotar la búsqueda)
        r1 = self.semantic.col_titulo.query(query_embeddings=[emb_q],   n_results=self.k)
        r2 = self.semantic.col_desc.query(query_embeddings=[emb_q],     n_results=self.k)
        r3 = self.semantic.col_headers.query(query_embeddings=[emb_q],  n_results=self.k)
        r4 = self.semantic.col_data.query(query_embeddings=[emb_q],     n_results=self.k)

        # 3) Unión de IDs candidatos
        ids1 = r1["ids"][0]
        ids2 = r2["ids"][0]
        ids3 = r3["ids"][0]
        ids4 = r4["ids"][0]
        candidate_ids = set(ids1 + ids2 + ids3 + ids4)
        print(f"[KEYWORD] {len(candidate_ids)} candidatos tras unión de colecciones")
        print(candidate_ids)
        
        # 4) Para cada candidato, recuperar sus 4 embeddings y calcular coseno
        similitudes = []
        for _id in candidate_ids:
            # recuperar embeddings
            emb_title = np.array(self.semantic.col_titulo.get(
                ids=[_id], include=["embeddings"]
            )["embeddings"][0])
            emb_desc = np.array(self.semantic.col_desc.get(
                ids=[_id], include=["embeddings"]
            )["embeddings"][0])
            emb_header = np.array(self.semantic.col_headers.get(
                ids=[_id], include=["embeddings"]
            )["embeddings"][0])
            emb_rows = np.array(self.semantic.col_data.get(
                ids=[_id], include=["embeddings"]
            )["embeddings"][0])

            # similitud coseno
            sim_title = cosine_similarity([emb_q], [emb_title])[0][0]
            sim_desc  = cosine_similarity([emb_q], [emb_desc  ])[0][0]
            sim_head  = cosine_similarity([emb_q], [emb_header])[0][0]
            sim_rows  = cosine_similarity([emb_q], [emb_rows  ])[0][0]

            # combinación ponderada
            sim_total = (
                self.pesos["title"]       * sim_title +
                self.pesos["description"] * sim_desc  +
                self.pesos["header"]      * sim_head  +
                self.pesos["rows"]        * sim_rows
            )

            print("Similitud total: ", sim_total)
            
            if sim_total >= self.umbral_similitud:
                similitudes.append({
                    "id": _id,
                    "sim_total": sim_total,
                    "sim_title": sim_title,
                    "sim_description": sim_desc,
                    "sim_header": sim_head,
                    "sim_rows": sim_rows
                })

        # 5) Orden descendente y quedarnos con top_n
        similitudes.sort(key=lambda x: x["sim_total"], reverse=True)
        top = similitudes[:self.top_n]

        # 6) Recuperar metadata de los top resultados y anotar puntuaciones
        hits = []
        for entry in top:
            _id = entry["id"]
            # getItems devuelve {'hits': [ {...} ], 'total': ...}
            doc = self.db.getItems([_id])["hits"][0]
            # añadimos las similitudes al objeto
            doc["score"]            = entry["sim_total"]
            doc["sim_title"]        = entry["sim_title"]
            doc["sim_description"]  = entry["sim_description"]
            doc["sim_header"]       = entry["sim_header"]
            doc["sim_rows"]         = entry["sim_rows"]
            hits.append(doc)

        reranked_hits = self.semantic.resReranker(query, hits)

        # Agregar campos json/csv aunque estén vacíos
        for r in reranked_hits:
            r['json'] = r.get('json', '')
            r['csv'] = r.get('csv', '')

        if not reranked_hits:
            print(f"[KEYWORD] Sin resultados, generando respuesta vacía.")
            return {
                "type": "keywords",
                "total": {"value": 0},
                "hits": [],
                "intro": self.generative.generateNoResultsResponse(query),
                "additional": ''
            }
        else:
            return {
                "type": "keywords",
                "total": {"value": len(reranked_hits)},
                "hits": reranked_hits,
                "intro": "",
                "additional": self.generative.additionalInfo(query)
            }
