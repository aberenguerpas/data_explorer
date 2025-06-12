import json
import chromadb

# Singleton para hacer una unificar las instancias de los índices
class dbEngine:
    _instance = None

    def __new__(cls, path="./chroma_data"):
        if cls._instance is None:
            cls._instance = super(dbEngine, cls).__new__(cls)
            cls._instance._initialize(path)
        return cls._instance

    # Inicialización y recuperación de los índices al cargar para no tener que volver a hacerlo    
    def _initialize(self, path):
        self.client = chromadb.PersistentClient(path=path)
        self.collections = {
            'datasets': self.client.get_or_create_collection(name='datasets'),
            'titulos': self.client.get_or_create_collection(name='titulos'),
            'descripciones': self.client.get_or_create_collection(name='descripciones'),
            'cabeceras_csv': self.client.get_or_create_collection(name='cabeceras_csv'),
            'contenido_csv': self.client.get_or_create_collection(name='contenido_csv')
        }
        # Log del tamaño de las colecciones
        for name, coll in self.collections.items():
            print(f"[CHROMA] Collection {name}: {coll.count()} documents")

    def get_client(self):
        return self.client

    def get_collection(self, name):
        return self.collections.get(name)

    def get_all_collections(self):
        return self.collections

    def getItem(self, identifier):
        res = self.collections['titulos'].get(ids=[identifier], include=["metadatas"])
        if res["metadatas"]:
            return {
                "hits": [{"_source": res["metadatas"][0]}],
                "total": {"value": 1}
            }
        return {"hits": [], "total": {"value": 0}}

    # Función para recuperar varios datasets a la vez con una lista de IDs
    def getItems(self, ids):
        if not ids:
            return {"total": {"value": 0}, "hits": []}

        # Recupera los datasets completos y formato la salida
        datasets_res = self.collections['datasets'].get(ids=ids, include=["metadatas"])
        
        hits = []
        for idx, identifier in enumerate(datasets_res.get("ids", [])):
            meta = datasets_res["metadatas"][idx]
            json_str = meta.get("json", "")
            csv_str = meta.get("csv", "")
            try:
                json_data = json.loads(json_str)
            except:
                json_data = {}
        
            hits.append({
                "title": json_data.get("title", ""),
                "description": json_data.get("description", ""),
                "id": identifier,
                "json": json_str,
                "csv": csv_str
            })
        
        return {"total": {"value": len(hits)}, "hits": hits}
