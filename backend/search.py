import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DATA_PATH = '../datos/'
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model.max_seq_length = 512

index_title = faiss.read_index("./indexs/titles.index")

while(True):
    print("**************************")
    texto = input("Buscar:")
    print("**************************")

    embs = np.array([model.encode(texto)])
    faiss.normalize_L2(embs)
    distances, ann = index_title.search(np.array(embs), k=10)

    for i, id in enumerate(ann[0]):
        f = open(DATA_PATH + "meta_"+str(id)+".json")
        data = json.load(f)
        print(data['title'], distances[0][i])
