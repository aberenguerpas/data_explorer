from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from search import SearchEngine
from logger import LoggerOpenSeach
from db import dbEngine
from generative import GenerativeEngine
from semantic import SemanticEngine
import json, csv
import pandas as pd
from io import StringIO
from json import loads
import time
from pyinstrument import Profiler

app = FastAPI()

generative = GenerativeEngine('gpt-4.1-nano')
db = dbEngine()
semantic = SemanticEngine('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', db)
log = LoggerOpenSeach()

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
    profiler = Profiler()
    profiler.start()

    start = time.time()
    r = search.search(q)
    end = time.time()
    response_time = end - start

    profiler.stop()
    log.saveLog(q, response_time)

    r['response_time'] = round(response_time, 3)
    
    with open("profile_output.html", "w") as f:
        f.write(profiler.output_html())

    return r

@app.get("/dataset/{item_id}")
def read_item(item_id: str):
    coleccion_titulos = db.get_collection("titulos")
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
    coleccion_contenido = db.get_collection("contenido_csv")
    result = coleccion_contenido.get(ids=[item_id])
    if result and result['metadatas']:
        try:
            csv_text = result['metadatas'][0].get("csv", "")
            if not csv_text:
                return {"response": "No hay datos"}
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(csv_text).delimiter
            return {"response": loads(pd.read_csv(StringIO(csv_text), engine='python',
                             on_bad_lines="skip", encoding='utf-8', sep=delimiter).to_json(orient="index")) if csv_text else "No data"}
        except:
            return {"response": "Error al recuperar contenido"}
    return {"response": "No encontrado"}

@app.get("/similar")
def read_item(q: str):
    return semantic.similarItems(q)

    