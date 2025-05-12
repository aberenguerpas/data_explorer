from transformers import AutoModel
import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from sentence_transformers import SentenceTransformer
import chromadb
import unicodedata
import re
import string
import torch
import time

# ----------- CONFIGURACIÓN -----------
model_name = "jinaai/jina-embeddings-v2-base-es"
DATA_PATH = '../datos/datos.gob.es'
CHROMA_PATH = "./chroma_data"
BLOCK_SIZE = 25

# ----------- NORMALIZACIÓN -----------
def normalize(text):
    if text is None:
        return ''
        
    split_words = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', text)).split()
    text = ' '.join(split_words)
    text = text.translate(str.maketrans('_-/', '   '))
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    
    text = ' '.join(text.split())
    text = re.sub(r'(?<!\d)[;,()]|[;,()](?!\d)', '', text)
    return text.lower()

# ----------- INICIALIZAR CHROMA -----------
client = chromadb.PersistentClient(path=CHROMA_PATH)
col_titulo = client.get_or_create_collection(name="titulos")
col_desc = client.get_or_create_collection(name="descripciones")
col_headers = client.get_or_create_collection(name="cabeceras_csv")
col_data = client.get_or_create_collection(name="contenido_csv")

# ----------- RECOLECCIÓN DE DATOS -----------
# Lee todos los ficheros de metadatos y el primer recurso csv para cada uno
def recolectar_datos_json(ruta_json, directorio, normalizado=True, num_rows=None):
    datos_recolectados = []
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos_json = json.load(f)

        norm = normalize if normalizado else (lambda x: x)

        uid = str(datos_json.get("identifier", "")).strip()
        
        titulo = norm(datos_json.get("title", "").strip())
        descripcion = norm(datos_json.get("description", "").strip())

        contador = 0
        for recurso in datos_json.get("resources", []):
            if recurso.get("format", "").lower() != "csv" or "path" not in recurso:
                    continue

            nombre_csv = os.path.basename(recurso["path"]).strip()
            ruta_csv = os.path.join(directorio, nombre_csv)
            
            if not os.path.exists(ruta_csv):
                continue

            try:
                df = pd.read_csv(ruta_csv, on_bad_lines='skip', encoding='utf-8', low_memory=False)
                if df.empty or df.columns.size == 0:
                    continue

                header_text = ' '.join([norm(str(col)) for col in df.columns])
                    
                if num_rows is not None:
                    df = df.sample(n=min(num_rows, len(df)), random_state=1)

                row_texts = df.astype(str).apply(lambda row: ' '.join([norm(v) for v in row if v.strip()]), axis=1)
                row_texts = row_texts[row_texts.str.strip().astype(bool)].tolist()

                with open(ruta_csv, "r", encoding="utf-8") as f:
                    contenido_csv = f.read()

                uid = uid + str(contador)
                contador += 1
                datos_recolectados.append({
                    "uid": uid,
                    "nombre_csv": nombre_csv,
                    "titulo": titulo,
                    "descripcion": descripcion,
                    "header_text": header_text,
                    "contenido_text": row_texts,
                    "json_raw": json.dumps(datos_json, ensure_ascii=False),
                    "csv_raw": contenido_csv
                })
                break
            except Exception as e:
                print(f"[!] Error leyendo CSV {ruta_csv}: {e}")

    except Exception as e:
        print(f"[!] Error procesando {ruta_json}: {e}")
    return datos_recolectados

# Lee todos los ficheros de metadatos y los recorre paralelamente sacando los datos de cada uno
def recolectar_todo(directorio, normalizado=True, num_tablas=None, num_rows=None):
    archivos = os.listdir(directorio)
    metadatos_json = [f for f in archivos if f.endswith(".json") and f.startswith("meta_")]
    if num_tablas:
        metadatos_json = metadatos_json[:num_tablas]

    rutas_json = [os.path.join(directorio, f) for f in metadatos_json]

    all_data = []
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for datos in tqdm(
            executor.map(lambda ruta: recolectar_datos_json(ruta, directorio, normalizado, num_rows), rutas_json),
            total=len(rutas_json), desc="Recolectando datos"
        ):
            all_data.extend(datos)
    return all_data

# ----------- GENERACIÓN E INDEXACIÓN DE EMBEDDINGS -----------
def generar_embeddings_y_guardar(data, model, BATCH_SIZE=64):
    ids = [d["uid"] for d in data]
    metas = [{"json": d["json_raw"], "csv": d["csv_raw"]} for d in data]
    
    titles = [d["titulo"] for d in data]
    descs = [d["descripcion"] for d in data]
    headers = [d["header_text"] for d in data]
    row_texts_all = [d["contenido_text"] for d in data]
    row_texts_all_fix = [' '.join(d["contenido_text"]) for d in data]

    emb_titles = model.encode(titles, batch_size=BATCH_SIZE)
    emb_descs = model.encode(descs, batch_size=BATCH_SIZE)
    emb_headers = model.encode(headers, batch_size=BATCH_SIZE)

    embedding_dim = emb_titles.shape[1]
    emb_rows_mean = []
    for row_texts in row_texts_all:
        if row_texts:
            try:
                row_embs = model.encode(row_texts, batch_size=1)
                emb_rows_mean.append(np.mean(row_embs, axis=0))

                del row_embs
                torch.cuda.empty_cache()
            except Exception as e:
                print(f"[!] Error en codificación de filas: {e}")
                emb_rows_mean.append(np.zeros(embedding_dim, dtype=np.float32))
        else:
            emb_rows_mean.append(np.zeros(embedding_dim, dtype=np.float32))

    print("Indexando en ChromaDB...")
    col_titulo.add(ids=ids, embeddings=emb_titles.tolist(), documents=titles, metadatas=metas)
    col_desc.add(ids=ids, embeddings=emb_descs.tolist(), documents=descs, metadatas=metas)
    col_headers.add(ids=ids, embeddings=emb_headers.tolist(), documents=headers, metadatas=metas)
    col_data.add(ids=ids, embeddings=emb_rows_mean, documents=row_texts_all_fix, metadatas=metas)

    del ids, metas, titles, descs, headers, row_texts_all, row_texts_all_fix, emb_titles, emb_descs, emb_headers, embedding_dim, emb_rows_mean
    torch.cuda.empty_cache()
    
    print("✔ Indexación finalizada")

# ----------- EJECUCIÓN PRINCIPAL -----------
if __name__ == "__main__":
    torch.cuda.empty_cache()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model_name = "jinaai/jina-embeddings-v2-base-es"
    model = SentenceTransformer(model_name, device=device)

    print("Recolectando datos...")
    datos = recolectar_todo(DATA_PATH, normalizado=True, num_rows=10)
    print(f"Total datasets recolectados: {len(datos)}")
    
    for i in range(0, len(datos), BLOCK_SIZE):
        bloque = datos[i:i+BLOCK_SIZE]
        print(f"- Procesando bloque {i//BLOCK_SIZE + 1} ({len(bloque)} elementos)...")
        inicio = time.time()
        try:
            generar_embeddings_y_guardar(bloque, model)
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                print("[!] Error de memoria en bloque:")
                for j, item in enumerate(bloque):
                    print(f"  - Item {j} UID: {item.get('uid', 'N/A')}")
                    print(f"    Título: {item.get('titulo', '')}")
                    print(f"    Descripción: {item.get('descripcion', '')}")
                    print(f"    Header: {item.get('header_text', '')[:100]}...")
                    print(f"    Contenido (primeras 200 chars): {' '.join(item.get('contenido_text', [])[:3])[:200]}...\n")
                torch.cuda.empty_cache()
                continue
            else:
                raise e
        print(f"-- Tiempo de ejecución: {time.time() - inicio:.2f} segundos.")
        torch.cuda.empty_cache()
