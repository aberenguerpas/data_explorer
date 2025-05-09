from opensearchpy import OpenSearch, RequestsHttpConnection
import json

host = 'search-inferia-datosgobes-4nwj2yk3cjasu3iiuaer4jcq6u.eu-west-3.es.amazonaws.com'
auth = ('alberto_infer_gob27', '#Centauro07')

client = OpenSearch(
        hosts=[{'host': host, 'port': 443}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

if not client.indices.exists('datosgobes'):
    f = open('schema.json')
    body = json.load(f)
    client.indices.create('datosgobes', body=body)
    f.close()
