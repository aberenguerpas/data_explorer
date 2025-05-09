from opensearchpy import OpenSearch, RequestsHttpConnection

class dbEngine:
    def __init__(self, db_name):
        self.db_name = db_name
        self.client = OpenSearch(
        hosts=[{'host': 'search-inferia-datosgobes-4nwj2yk3cjasu3iiuaer4jcq6u.eu-west-3.es.amazonaws.com',
                'port': 443}],
        http_auth=('alberto_infer_gob27', 'Inferia4Real_'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
        )
        
    def getItems(self, id):
        query = {
            'query': {
                'terms': {
                    'id_custom': id
                }
            },
            "fields": [
                "title",
                "description",
                "id_custom"
            ],
            "_source": False
        }
        response = self.client.search(
            body=query,
            index=self.db_name
        )
        return response['hits']
    
    def getItem(self, id):

        query = {
            'query': {
                'match': {
                    'id_custom': id
                }
            },
        }
        response = self.client.search(
            body=query,
            index=self.db_name
        )
        return response['hits']