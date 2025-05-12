import pickle
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

class SearchEngine:
    def __init__(self, db, generative, semantic):
        print('Created Search Engine')
        
        self.model_name = "meta-llama/Llama-3.2-3B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_auth_token=True)
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            self.model_name, device_map="auto", torch_dtype="auto", use_auth_token=True
        )
        self.classifier_pipeline = pipeline("text-generation", model=self.llm_model, tokenizer=self.tokenizer)

        self.db = db
        self.generative = generative
        self.semantic = semantic

    def search(self, text):
        print(f"[SEARCH] Consulta recibida: {text}")
        query_type = self.classify_query_type(text)
        print(f"[SEARCH] Tipo de consulta clasificada: {'intent' if query_type == 1 else 'keyword'}")
        if query_type == 1:
            keywords = self.generative.getKeywords(text)
            print(f"[SEARCH] Keywords generadas: {keywords}")
            return self.get_intent_results(keywords, text)
        else:
            return self.get_keyword_results(text)

    def get_intent_results(self, queries, intent):
        resultados_finales = []
        total_hits = 0
        ya_encontrados = set()

        for q in queries['keywords']:
            query = q['consulta']
            print(f"[INTENT] Ejecutando consulta: '{query}'")
            r1, r2, r3, r4 = self.semantic.query_collections(query, k=10)

            def get_score_dict(r):
                print(f"[INTENT] Resultados recibidos para '{query}': {r['ids']}")
                return {r['ids'][0][i]: r['distances'][0][i] for i in range(len(r['ids'][0]))}

            scores1 = get_score_dict(r1)
            scores2 = get_score_dict(r2)
            scores3 = get_score_dict(r3)
            scores4 = get_score_dict(r4)

            all_ids = set(scores1.keys()) | set(scores2.keys()) | set(scores3.keys()) | set(scores4.keys())
            print(f"[INTENT] Todos los IDs encontrados: {all_ids}")
            combined_scores = {}
            
            for id in all_ids:
                # ponderación de scores
                if id in scores1 and id in scores2 and id in scores3 and id in scores4:
                    score = scores1[id] * 0.5 + scores2[id] * 0.3 + scores3[id] * 0.1 + scores4[id] * 0.1
                elif id in scores2 and id in scores3:
                    score = scores2[id] * 0.75 + scores3[id] * 0.25
                elif id in scores1 and id in scores2:
                    score = scores1[id] * 0.65 + scores2[id] * 0.35
                elif id in scores1 and id in scores3:
                    score = scores1[id] * 0.85 + scores3[id] * 0.15
                else:
                    score = scores1.get(id, 0) + scores2.get(id, 0) + scores3.get(id, 0) + scores4.get(id, 0)
                print("Puntuacion : ", score)
                if score > 0.8:
                    combined_scores[id] = score

            ids_ordenados = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
            ids_finales = [id for id, _ in ids_ordenados]
            print(f"[INTENT] IDs seleccionados (score > 0.8): {ids_finales}")

            resultados = self.db.getItems(ids_finales)
            hits = resultados.get('hits', [])
            print(f"[INTENT] Resultados base: {[r.get('id') for r in hits]}")

            reranked_hits = self.semantic.resReranker(query, hits)
            print(f"[INTENT] Resultados tras rerank: {[r.get('id') for r in reranked_hits]}")

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
                'type': 'intent',
                'total': 0,
                'hits': 0,
                'intro': self.generative.generateNoResultsResponse(intent),
                'additional': ''
            }

        return {
            'type': 'intent',
            'total': total_hits,
            'hits': resultados_finales,
            'intro': queries['intro'],
            'additional': queries['extra']
        }

    def get_keyword_results(self, query):
        print(f"[KEYWORD] Ejecutando búsqueda directa: '{query}'")
        r1, r2, r3, r4 = self.semantic.query_collections(query, k=50)

        def get_score_dict(r):
            print(f"[KEYWORD] IDs obtenidos: {r['ids']}")
            return {r['ids'][0][i]: r['distances'][0][i] for i in range(len(r['ids'][0]))}

        scores1 = get_score_dict(r1)
        scores2 = get_score_dict(r2)
        scores3 = get_score_dict(r3)
        scores4 = get_score_dict(r4)

        all_ids = set(scores1.keys()) | set(scores2.keys()) | set(scores3.keys()) | set(scores4.keys())
        print(f"[KEYWORD] Total IDs únicos encontrados: {len(all_ids)}")
        scores = {}

        for id in all_ids:
            if id in scores1 and id in scores2 and id in scores3 and id in scores4:
                score = scores1[id] * 0.5 + scores2[id] * 0.3 + scores3[id] * 0.1 + scores4[id] * 0.1
            elif id in scores2 and id in scores3:
                score = scores2[id] * 0.75 + scores3[id] * 0.25
            elif id in scores1 and id in scores2:
                score = scores1[id] * 0.65 + scores2[id] * 0.35
            elif id in scores1 and id in scores3:
                score = scores1[id] * 0.85 + scores3[id] * 0.15
            else:
                score = scores1.get(id, 0) + scores2.get(id, 0) + scores3.get(id, 0) + scores4.get(id, 0)
            print("Puntuacion : ", score)

            if score > 0.8:
                scores[id] = score

        ids_ordenados = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        ids_finales = [id for id, _ in ids_ordenados]
        print(f"[KEYWORD] IDs seleccionados (score > 0.8): {ids_finales}")

        response = self.db.getItems(ids_finales)
        response['type'] = 'keywords'

        for r in response.get('hits', []):
            r['json'] = r.get('json', '')
            r['csv'] = r.get('csv', '')

        if response['total']['value'] == 0:
            print(f"[KEYWORD] Sin resultados, generando respuesta vacía.")
            response['intro'] = self.generative.generateNoResultsResponse(query)
            response['additional'] = ''
        else:
            print(f"[KEYWORD] Aplicando reranker...")
            response['hits'] = self.semantic.resReranker(query, response['hits'])
            if not response['hits']:
                print(f"[KEYWORD] Reranker eliminó todos los resultados.")
                response['intro'] = self.generative.generateNoResultsResponse(query)
                response['total']['value'] = 0
            else:
                response['additional'] = self.generative.additionalInfo(query)

        return response

    def classify_query_type(self, query):
        prompt = f"""
Dada la siguiente consulta de un usuario, determina si se trata de una búsqueda directa de información (tipo 'keyword') o si el usuario está expresando una intención más general o abstracta (tipo 'intent').

- Si el usuario menciona una acción, un objetivo o una necesidad, responde con: intent.
- Si el usuario menciona directamente un concepto, entidad, evento o término específico a buscar, responde con: keyword.

Devuelve solo una de estas dos palabras: intent o keyword.

Consulta: "{query}"
Respuesta:
""".strip()

        print(f"[CLASSIFY] Prompt de clasificación:\n{prompt}")
        result = self.classifier_pipeline(prompt, max_new_tokens=10, return_full_text=False)[0]['generated_text'].strip().lower()
        print(f"[CLASSIFY] Resultado clasificación: {result}")
        return 0 if "keyword" in result else 1
