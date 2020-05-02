from elasticsearch import helpers
from elasticsearch import Elasticsearch


elastic_url = "localhost"


def get_elastic():
    return Elasticsearch([elastic_url + ':9200'], timeout=30)


def elastic(doc, index, type):
    esclient = get_elastic()

    statcnt = 0
    actions = []

    for row in doc:
        actions.append({
            "_op_type": "index",
            "_index": index,
            "_type": type,
            "_source": row
        })

    for ok, response in helpers.streaming_bulk(esclient, actions, index=index, doc_type=type,
                                               max_retries=5,
                                               raise_on_error=False, raise_on_exception=False):
        if not ok:
            statcnt+=0
            print(response)
        else:
            statcnt += 1

    return statcnt
