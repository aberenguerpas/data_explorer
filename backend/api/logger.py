from opensearchpy import OpenSearch, RequestsHttpConnection
from datetime import datetime

class LoggerOpenSeach():
    def __init__(self):
        self.client = OpenSearch(
                hosts=[{'host': 'search-inferia-datosgobes-4nwj2yk3cjasu3iiuaer4jcq6u.eu-west-3.es.amazonaws.com'
                        ,'port': 443}],
                http_auth=('alberto_infer_gob27', 'Inferia4Real_'),
                use_ssl=True,
                verify_certs=True,
                connection_class=RequestsHttpConnection
        )
        
    def saveLog(self, query, time):
        document = {
            'query': query,
            'response_time': time,
            'date': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }

        self.client.index(
            index = 'log-queries',
            body = document,
            refresh = True
        )
        