from sentence_transformers import SentenceTransformer
from db import dbEngine
from FlagEmbedding import FlagReranker
import faiss
import os
import numpy as np

class SemanticEngine:
    def __init__(self, model_name):
        print('Created Semantic Engine')
        os.environ["TOKENIZERS_PARALLELISM"] = "true"

        self.model = SentenceTransformer(model_name)
        self.reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation
        self.db = dbEngine('datosgobes')
        self.model.max_seq_length = 512
        self.index_title = faiss.read_index("../indexs/titles.index")
        self.index_desc = faiss.read_index("../indexs/desc.index")
        self.index_data = faiss.read_index("../indexs/data.index")
        

    def similarItems(self, query):
        embs = np.array([self.model.encode(query)])
        faiss.normalize_L2(embs)
        distances, ann = self.index_title.search(np.array(embs), k=4)
        
        items = self.db.getItems(ann[0][1:])
        for i, _ in enumerate(items['hits']):
            items['hits'][i]['_score'] = float(distances[0][i])
        return items

    def resReranker(self, q, list_results):
        rank_description = []
        final_result = []

        for r in list_results:
            rank_description.append([q, r['fields']['description'][0]])

        scores_description = self.reranker.compute_score(rank_description, normalize=True)
        # Si solo hay un resultado
        if type(scores_description) == np.float64:
            scores_description = [scores_description]
            
        for index, score in enumerate(scores_description):
            if score >= 0.02:
                final_result.append(list_results[index])

        return final_result
    
    