from flask import Flask, request
from flask_cors import CORS
from biobert_embedding.embedding import BiobertEmbedding
from elasticsearch import Elasticsearch
import sys
from timeit import default_timer as timer

# Define the app
app = Flask(__name__)
# Load configs
app.config.from_object('config')
# Set CORS policies
CORS(app)

biobert = BiobertEmbedding()


def connectElastic(ip, port):
    # Connect to an elasticsearch node with the given ip and port
    esConn = None

    esConn = Elasticsearch([{"host": ip, "port": port}])
    if esConn.ping():
        print("Connected to elasticsearch...")
    else:
        print("Elasticsearch connection error..")
        sys.exit(1)

    return esConn

# Connect to es node
esConn = connectElastic(app.config['ELASTIC_IP'], app.config['ELASTIC_PORT'])

@app.route("/query", methods=["GET"])
def qa():
    # API to return top_n matched records for a given query
    if request.args.get("query"):
        # Generate embeddings for the input query
        queryTensor = biobert.sentence_vector(request.args.get("query"))
        queryVec = queryTensor.numpy()

        # Retrieve the semantically similar records for the query
        records = semanticSearch(queryVec, app.config['ELASTIC_INDEX'], app.config['SEARCH_THRESH'])
    else:
        return {"error": "Couldn't process your request"}, 422
    return {"data": records}

def semanticSearch(queryVec, index, thresh=1.2, top_n=10):
    # Retrieve top_n semantically similar records for the given query vector
    if not esConn.indices.exists(index):
        return "No records found"
    s_body = {
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'description_vec') + 1.0",
                    "params": {"query_vector": queryVec}
                }
            }
        }
    }
    # Semantic vector search with cosine similarity
    start = timer()
    result = esConn.search(index=index, body=s_body)
    end = timer()
    searchTime = end - start
    print (end - start)

    total_match = len(result["hits"]["hits"])
    print("Total Matches: ", str(total_match))
    data = []
    data.append({'search_time': searchTime})
    if total_match > 0:
        row_ids = []
        for hit in result["hits"]["hits"]:
            if hit['_score'] > thresh and hit['_source']['row_id'] not in row_ids and len(data) <= top_n:
                print("--\nscore: {} \n variable_id: {} \n description: {}\n--".format(hit["_score"], hit["_source"]['variable_id'], hit["_source"]['description']))
                row_ids.append(hit['_source']['row_id'])
                data.append({'description': hit["_source"]['description'], 'variable_id': hit["_source"]['variable_id']})
    return data

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
