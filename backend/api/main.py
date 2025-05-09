import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from search import SearchEngine
from logger import LoggerOpenSeach
from db import dbEngine
from generative import GenerativeEngine
from semantic import SemanticEngine
from utils import load_dataset

app = FastAPI()

generative = GenerativeEngine('gpt-4-turbo')
semantic = SemanticEngine('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
log = LoggerOpenSeach()
db = dbEngine('datosgobes')

search = SearchEngine(db, generative, semantic)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def searchApi(q: str):
    start = time.time()
    r = search.search(q)
    end = time.time()
    total_time = end-start
    log.saveLog(q, total_time)
    return r

@app.get("/dataset/{item_id}")
def read_item(item_id: str):
    return db.getItem(item_id)

@app.get("/dataset/{item_id}/suggestions")
def get_suggestions(item_id: str):
    return generative.suggestions(item_id, db)

@app.get("/dataset/{item_id}/sample")
def download_sample(item_id: str):
    if os.path.exists('../../datos/'+item_id+'.csv'):
        try:
            return {"response": load_dataset(item_id)}
        except Exception as e:
            return {"response": "Error parsing"}
    else:
        return {"response": "Error parsing"}

@app.get("/similar")
def read_item(q: str):
    return semantic.similarItems(q)
