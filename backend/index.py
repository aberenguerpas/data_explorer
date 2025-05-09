import os
import json
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

DATA_PATH = '../datos/'

files = os.listdir(DATA_PATH)
torch.set_num_threads(4)

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model.max_seq_length = 512

index_title = faiss.IndexIDMap(faiss.IndexFlatIP(384))
index_desc = faiss.IndexIDMap(faiss.IndexFlatIP(384))
index_data = faiss.IndexIDMap(faiss.IndexFlatIP(384))

json_files = [filename for filename in files if filename.endswith('.json')]

for file in tqdm(json_files):
    f = open(DATA_PATH + file)
    data = json.load(f)

    # index title
    embs = np.array([model.encode(data['title'])])
    faiss.normalize_L2(embs)
    index_title.add_with_ids(embs, np.array(data['id_custom']))

    # index desc
    embs = np.array([model.encode(data['description'])])
    faiss.normalize_L2(embs)
    index_desc.add_with_ids(embs, np.array(data['id_custom']))

    # index data
    if os.path.exists(DATA_PATH+data['id_custom']+".csv"):
        f2 = open(DATA_PATH+data['id_custom']+".csv", "r")
        df = f2.read()
        embs = np.array([model.encode(df)])
        faiss.normalize_L2(embs)
        index_data.add_with_ids(embs, np.array(data['id_custom']))


faiss.write_index(index_title, "./indexs/titles.index")
faiss.write_index(index_desc, "./indexs/desc.index")
faiss.write_index(index_data, "./indexs/data.index")
