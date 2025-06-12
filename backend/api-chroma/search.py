import pickle
import time

# He añadido esto para poder cambiar entre la petición a la API para la generación de la info adicional o la query de debajo.
flag_adiccional_generativo = False

RESPUESTA_ADICIONAL = "<p>Addicionalmente existen otras fuentes que pueden ser de utilidad:</p><br><p><a class='font-semibold underline' href='https://datos.gob.es/' target='_blank'>Datos Abiertos del Gobierno de España</a>: Plataforma con múltiples datasets públicos de diferentes ámbitos en España.<p><br>\n<p><a class='font-semibold underline' href='https://opendata.aragon.es/' target='_blank'>Open Data Aragón</a>: Datos abiertos de la comunidad autónoma de Aragón.<p><br>\n<p><a class='font-semibold underline' href='https://datos.madrid.es/' target='_blank'>Datos Abiertos del Ayuntamiento de Madrid</a>: Datos abiertos de la comunidad autónoma de Madrid.<p><br>\n<p><a class='font-semibold underline' href='https://opendata.jcyl.es/' target='_blank'>Datos Abiertos de Castilla y León</a>: Datos públicos de Castilla y León en diferentes ámbitos.<p><br>\n<p><a class='font-semibold underline' href='https://opendata.bcn.cat/' target='_blank'>Ajuntament de Barcelona Open Data</a>: Datos abiertos de la provincia Barcelona.<p><br>\n"

class SearchEngine:
    def __init__(self, db, generative, semantic):
        print('Created Search Engine')
        self.db = db
        self.query_classifier = pickle.load(open('/app/api-chroma/query_classifier.pickle', 'rb'))
        self.generative = generative
        self.semantic = semantic
        self.pesos = {
            "title": 0.5,
            "description": 0.3,
            "header": 0.1,
            "rows": 0.1
        }
        
        # Con 0.8 no encontraba nada, con 0.5 ha encontrado solo cosas relevantes
        self.umbral_similitud = 0.50
        self.umbral_similitud_generativo = 0.50
        self.top_n = 10 # Resultados devueltos por keyword
        self.k = 100    # Número de elementos máximo recuperado

    # Función del endpoint search (inicio de las busquedas), ramificación keyword - intención
    def search(self, text):
        print(f"[SEARCH] Consulta recibida: {text}")
        ini_query = time.time()
        query_type = self.query_classifier.predict(self.semantic.model.encode([text])).tolist()[0]
        print(f"[SEARCH] Tipo de consulta clasificada: {'intent' if query_type == 1 else 'keyword'}")
        print(f"[Tiempo Keyword-Intent] {time.time() - ini_query}")

        if query_type == 1:
            ini_get_keywords = time.time()
            # Según si queremos usar la API para generar la info adicional o no, la función con getKeywords_extra genera y devuelve un extra, mientras que la otra no.
            if flag_adiccional_generativo:
                keywords = self.generative.getKeywords_extra(text)
            else:
                keywords = self.generative.getKeywords(text)

            print(f"[Tiempo Generar-Keywords] {time.time() - ini_get_keywords}")

            print(f"[SEARCH] Keywords generadas: {keywords}")
            return self.get_intent_results(keywords, text)
        else:
            return self.get_keyword_results(text)
    
    # Función para únifica la busqueda. Hace la query, filtro de similitud y rerank
    def search_single_query(self, query, threshold=None, limit=None):        
        ini_query = time.time()
        # Consulta y devuelve todas las coincidencias en chroma
        titulos, descripciones, cabeceras_csv, contenido_csv = self.semantic.query_collections(query, k=self.k)
        candidate_ids = set(titulos["ids"]) | set(descripciones["ids"]) | set(cabeceras_csv["ids"]) | set(contenido_csv["ids"])       
        print(f"[Tiempo Query] {time.time() - ini_query}")

        print(f"[QUERY INICIAL] {len(candidate_ids)} candidatos tras unión de colecciones")
        
        # Ponderación de las similitudes
        ini_similitudes = time.time()
        similitudes = []
        for _id in candidate_ids:
            sim_total = 0
            sim_details = {}
            
            for name, weight in self.pesos.items():
                collection_name = {"title": "titulos","description": "descripciones", "header": "cabeceras_csv", "rows": "contenido_csv"}[name]
                collection = {"titulos": titulos,"descripciones": descripciones,"cabeceras_csv": cabeceras_csv,"contenido_csv": contenido_csv}[collection_name]
                
                if _id in collection["ids"]:
                    idx = collection["ids"].index(_id)
                    sim = collection["similarities"][idx]
                    sim_total += sim * weight
                    sim_details[f"sim_{name}"] = sim
                else:
                    sim_details[f"sim_{name}"] = 0

            if sim_total >= threshold:
                similitudes.append({
                    "id": _id,
                    "sim_total": sim_total,
                    **sim_details
                })
                
        if not similitudes:
            print(f"[FILTRO SIMILITUD] Ningún candidato supera el umbral {threshold}")
            return [], []

        # Ordenar y seleccionar top resultados
        similitudes.sort(key=lambda x: x["sim_total"], reverse=True)
        top = similitudes[:limit] if limit else similitudes
        top_ids = [entry["id"] for entry in top]
        print(f"[Tiempo Similitudes] {time.time() - ini_similitudes}")
        
        # Recuperar metadatos
        ini_recuperacion = time.time()
        docs = self.db.getItems(top_ids)["hits"]
        hits = []
        for i, doc in enumerate(docs):
            doc["score"] = top[i]["sim_total"]
            doc["sim_title"] = top[i]["sim_title"]
            doc["sim_description"] = top[i]["sim_description"]
            doc["sim_header"] = top[i]["sim_header"]
            doc["sim_rows"] = top[i]["sim_rows"]
            hits.append(doc)
        print(f"[Tiempo Recuperar Datos DB] {time.time() - ini_recuperacion}")

        # Aplicar reranking
        ini_rerank = time.time()
        print(f"[RERANKER] Total results after similarity: {len(hits)}")
        reranked_hits = self.semantic.resReranker(query, hits)
        print(f"[Tiempo Rerank] {time.time() - ini_rerank}")

        return reranked_hits, top

    def get_keyword_results(self, query):
        print(f"[KEYWORD] Ejecutando búsqueda manual para: '{query}'")
        reranked_hits, top = self.search_single_query(query, threshold=self.umbral_similitud, limit=self.top_n)
        
        # Asegurar campos json y csv
        for r in reranked_hits:
            r['json'] = r.get('json', '')
            r['csv'] = r.get('csv', '')

        if flag_adiccional_generativo:
            adaptativo = self.generative.additionalInfo(query)
        else:
            adaptativo = RESPUESTA_ADICIONAL
            
        if not reranked_hits:
            print(f"[KEYWORD] Sin resultados, generando respuesta vacía.")
            return {
                "type": "keywords",
                "total": {"value": 0},
                "hits": [],
                "intro": self.generative.generateNoResultsResponse(query),
                "additional": ''
            }
        return {
            "type": "keywords",
            "total": {"value": len(reranked_hits)},
            "hits": reranked_hits,
            "intro": "",
            "additional": adaptativo
        }

    def get_intent_results(self, queries, intent):
        print(f"[INTENT] Ejecutando búsqueda para la intención: '{intent}'")
        resultados_finales = []
        total_hits = 0
        ya_encontrados = set()

        if flag_adiccional_generativo:
            adaptativo = queries.get('extra', RESPUESTA_ADICIONAL)
        else:
            adaptativo = RESPUESTA_ADICIONAL
            
        for q in queries['keywords']:
            query = q['consulta']
            print(f"[INTENT] Ejecutando consulta para la keyword: '{query}'")
            reranked_hits, _ = self.search_single_query(query, threshold=self.umbral_similitud_generativo, limit=self.top_n)
            
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
            "additional": adaptativo
        }