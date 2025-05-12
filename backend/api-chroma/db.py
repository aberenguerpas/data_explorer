import json
import chromadb

class dbEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.titulos = self.client.get_or_create_collection(name="titulos")
        self.contenido = self.client.get_or_create_collection(name="contenido_csv")

    def getItem(self, identifier):
        res = self.titulos.get(ids=[identifier], include=["metadatas"])
        if res["metadatas"]:
            return {
                "hits": [{"_source": res["metadatas"][0]}],
                "total": {"value": 1}
            }
        else:
            return {"hits": [], "total": {"value": 0}}

    def getItems(self, ids):
        hits = []

        for identifier in ids:
            try:
                item = self.titulos.get(ids=[identifier], include=["metadatas"])
                meta = item["metadatas"][0] if item["metadatas"] else {}

                json_data = {}
                if "json" in meta:
                    json_data = json.loads(meta["json"])

                csv_res = self.contenido.get(ids=[identifier], include=["metadatas"])
                csv_meta = csv_res["metadatas"][0] if csv_res["metadatas"] else {}

                hit = {
                    "title": json_data.get("title", ""),
                    "description": json_data.get("description", ""),
                    "id": identifier,
                    "json": meta.get("json", ""),
                    "csv": csv_meta.get("csv", "")
                }

                hits.append(hit)

            except Exception as e:
                print(f"[!] Error procesando ID {identifier}: {e}")
                hits.append({
                    "title": "",
                    "description": "",
                    "id": identifier,
                    "json": "",
                    "csv": ""
                })

        return {
            "total": {"value": len(hits)},
            "hits": hits
        }
