from elasticsearch import helpers
from elasticsearch import Elasticsearch


def get_elastic():
    return Elasticsearch(['localhost:9200'], timeout=30)


def elastic(doc, index, type):
    es_client = get_elastic()

    statcnt = 0
    actions = []

    for row in doc:
        actions.append({
            "_op_type": "index",
            "_index": index,
            "_type": type,
            "_source": row
        })

    for ok, response in helpers.streaming_bulk(es_client, actions, index=index, doc_type=type,
                                               max_retries=5,
                                               raise_on_error=False, raise_on_exception=False):
        if not ok:
            statcnt += 0
            print(response)
        else:
            statcnt += 1

    return statcnt
