from opensearchpy import OpenSearch, RequestsHttpConnection
from tqdm import tqdm
import json
import os


def cleanKeyword(k):
    k = " ".join(k.split('-')).capitalize(),

    return k

host = 'search-inferia-datosgobes-4nwj2yk3cjasu3iiuaer4jcq6u.eu-west-3.es.amazonaws.com'
auth = ('alberto_infer_gob27', '#Centauro07')

client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
)

DATA_PATH = '../../datos/'

files = os.listdir(DATA_PATH)

for file in tqdm(files):
    f = open(DATA_PATH + file)
    data = json.load(f)

    doc = {
        "identifier": data['identifier'],
        "id_custom": data['id_custom'],
        "img": data['img'],
        "title": data['title'],
        "description": data['description'],
        "theme": [cleanKeyword(k) for k in data['theme']] if type(data['theme']) is list else [cleanKeyword(data['theme'])],
        "resources": [],
        "modified": data['modified'],
        "issued": data['issued'],
        "license": data['license'],
        "source": "datos.gob.es",
        "geo": data['geo'],
        "temporal": [
            {"startDate": data['temporal'].get('startDate', None), "endDate": data['temporal'].get('endDate', None)}
        ]
    }

    for r in data['resources']:
        doc['resources'].append({"name": r['name'],
                                "downloadUrl": r["downloadUrl"],
                                "mediaType": r["mediaType"],
                                "size": r.get("size", None)
                                })

    client.index(id=data['id_custom'], index='datosgobes', body=doc, refresh=True)
