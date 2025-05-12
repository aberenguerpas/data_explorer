from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from search import SearchEngine
from logger import LoggerOpenSeach
from db import dbEngine
from generative import GenerativeEngine
from semantic import SemanticEngine
import chromadb
import json
from transformers import AutoModel

app = FastAPI()

generative = GenerativeEngine('gpt-4.1-nano')

semantic = SemanticEngine('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
log = LoggerOpenSeach()
db = dbEngine()
search = SearchEngine(db, generative, semantic)

# Cliente Chroma
client = chromadb.PersistentClient(path="./chroma_data")

coleccion_titulos = client.get_or_create_collection(name="titulos")
coleccion_contenido = client.get_or_create_collection(name="contenido_csv")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def searchApi(q: str):
    import time
    start = time.time()
    r = search.search(q)
    end = time.time()
    log.saveLog(q, end - start)
    return r

@app.get("/dataset/{item_id}")
def read_item(item_id: str):
    result = coleccion_titulos.get(ids=[item_id])
    if result and result['metadatas']:
        try:
            return json.loads(result['metadatas'][0]['json'])
        except:
            return {"error": "Error decodificando JSON"}
    return {"error": "No encontrado"}

@app.get("/dataset/{item_id}/suggestions")
def get_suggestions(item_id: str):
    return generative.suggestions(item_id, db)

@app.get("/dataset/{item_id}/sample")
def download_sample(item_id: str):
    result = coleccion_contenido.get(ids=[item_id])
    if result and result['metadatas']:
        try:
            csv_text = result['metadatas'][0].get("csv", "")
            return {"response": csv_text if csv_text else "No data"}
        except:
            return {"response": "Error al recuperar contenido CSV"}
    return {"response": "No encontrado"}

@app.get("/similar")
def read_item(q: str):
    return semantic.similarItems(q)
