import pickle
import faiss
import numpy as np

class SearchEngine:
    def __init__(self, db, generative, semantic):
        print('Created Search Engine')
        self.query_classifier = pickle.load(open('./query_classifier.pickle', 'rb'))
        self.semantic = semantic
        self.generative = generative
        self.db = db

    # Descubrir si es búsqueda por keywords o el usuario quiere hacer algo
    def search(self, text):
        query_type = self.query_classifier.predict(self.semantic.model.encode([text])).tolist()[0]

        if query_type == 1:
            keywords = self.generative.getKeywords(text)
            return self.getResults(keywords, text)
        else:
            return self.searchKeywords(text)
        

    def getResults(self, queries, intent):
        res_final = []
        res_totales = 0
        for q in queries['keywords']:
            embs = np.array([self.semantic.model.encode(q['consulta'])])
            faiss.normalize_L2(embs)
            distances, ann = self.semantic.index_title.search(np.array(embs), k=10)

            res = [d for i, d in enumerate(ann[0]) if distances[0][i] > 0.7]

            q['resultados'] = self.db.getItems(res)
            if len(q['resultados']['hits'])>0:
                q['resultados']['hits'] = self.semantic.resReranker(q['consulta'], q['resultados']['hits'])

            res_totales += len(q['resultados']['hits'])
            if len(q['resultados']['hits'])>0:
                res_final.append(q)
        if res_totales==0:
            return {'type': 'intent', 'total': 0, 'hits': 0 ,'intro': self.generative.generateNoResultsResponse(intent), 'additional':''}
        else:
            return {'type': 'intent', 'total': res_totales, 'hits': res_final ,'intro': queries['intro'], 'additional': queries['extra']}


    def searchKeywords(self,q):
        embs = np.array([self.semantic.model.encode(q)])
        faiss.normalize_L2(embs)

        distances, ann = self.semantic.index_title.search(np.array(embs), k=50)
        r = {ann[0][i] : distances[0][i] for i, _ in enumerate(distances[0])}

        distances2, ann2 = self.semantic.index_desc.search(np.array(embs), k=50)
        r2 = {ann2[0][i] : distances2[0][i] for i, _ in enumerate(distances2[0])}

        distances3, ann3 = self.semantic.index_data.search(np.array(embs), k=50)
        r3 = {ann3[0][i] : distances3[0][i] for i, _ in enumerate(distances3[0])}

        ids = [*ann[0], *ann2[0], *ann3[0]]
        ids = list(dict.fromkeys(ids))

        res = []
        for id in ids:
            score = 0
            if id in r and id in r2 and id in r3:
                score = r.get(id, 0)*0.6 + r2.get(id, 0)*0.3 + r3.get(id, 0)*0.1
            elif id in r2 and id in r3:
                score = r2.get(id, 0)*0.75 + r3.get(id, 0)*0.25
            elif id in r and id in r2:
                score = r.get(id, 0)*0.65 + r2.get(id, 0)*0.35
            elif id in r and id in r3:
                score = r.get(id, 0)*0.85 + r3.get(id, 0)*0.15
            else:
                score = r.get(id, 0) + r2.get(id, 0) + r3.get(id, 0)

            res.append({id: score})

        # Merge the dictionaries
        merged_dict = {key: val for d in res for key, val in d.items()}

        # Filter the merged dictionary
        filtered_dict = {key: val for key, val in merged_dict.items() if val > 0.8}

        # Ordenar
        sorte = sorted(filtered_dict.items(), key=lambda x: x[1], reverse=True)

        res = [key for key, _ in sorte]
        
        response = self.db.getItems(res)

        response['type'] = 'keywords'
        
        if response['total']['value']==0:
            response['intro'] = self.generative.generateNoResultsResponse(q)
            response['additional'] = ''
        
        else:
            response['hits'] = self.semantic.resReranker(q, response['hits'])
    
            if len(response['hits']) == 0:
                response['intro'] = self.generative.generateNoResultsResponse(q)
                response['total']['value']= 0
            else:
                response['additional'] = self.generative.additionalInfo(q)

        return response
