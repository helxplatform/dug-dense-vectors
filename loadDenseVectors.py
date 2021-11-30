import argparse
from xml.etree import ElementTree as ET
import config
from biobert_embedding.embedding import BiobertEmbedding
from pathlib import Path
from elasticsearch import Elasticsearch
import sys

########################################################################################
#
# This code creates connects to an ElasticSearch instance and creates an index specified 
# with the indexName parameter.  It then reads file in the directory tree specified by
# the inputDir parameter and extracts information. Currently the files have to be
# XML files that contain fields that are hard-coded in this code, but that restriction
# will eventually have to be lifted.  The information is as an input to the Biobert
# sentence embedding module and the resulting vector is passed as part of the input
# from documents in the index. See 
#
#  https://blog.accubits.com/vector-similarity-search-using-elasticsearch/
#
# for some insight into this process.
########################################################################################

def main(args):

   # Extract command line args
   indexName = args.indexName
   inputDir = Path(args.inputDir)

   # Connect to elasticSearch
   esConn = connectElastic(config.ELASTIC_IP, config.ELASTIC_PORT)

   # Create the index. Note it's currently OK if the index is already there.  We should
   # probably add a command line option to delete the index if it's already there
   createIndex(indexName, esConn)

   # Get a list of all of the xml files under the inputDir
   # Note that for some reason the bdc_dbgap_data_dicts.tar.gz file
   # contains one "." hidden file for each regular files.  Those
   # files don't seem to be valid xml, which accounts for the "[!.]" in the glob
   fileList = [f for f in inputDir.resolve().glob('**/[!.]*.xml') if f.is_file()]
   insertDataIntoIndex(fileList, indexName, esConn)

def insertDataIntoIndex(fileList, indexName, esConn):
    # Get biobert
    biobert = BiobertEmbedding()
    rowId = 1

    for filePath in fileList:
       fileName = str(filePath)
       print(fileName)
       tree = ET.parse(fileName)
       root = tree.getroot()
       for variable in root.iter('variable'):
          varId = variable.attrib['id']
          description = variable.find('description').text
          name = variable.find('name').text
          print(f"varId: {varId}, name: {name}, description: {description}")
          sentenceEmbedding = biobert.sentence_vector(description)
          sentenceArray = sentenceEmbedding.numpy()
          insertBody = {'variable_id': f"{varId} {name}",
                        'description': description,
                        'description_vec':  sentenceArray,
                        'row_id':  rowId }
          rowId += 1
          esConn.index(index=indexName, body=insertBody)
    print(f"number of rows inserted is {rowId - 1}")

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

def createIndex(indexName, esConn):
    # Define the index mapping
    indexBody = {
        "mappings": {
            "properties": {
                "variable_id": {
                    "type": "text"
                },
                "description": {
                    "type": "text"
                },
                "description_vec": {
                    "type": "dense_vector",
                    "dims": 768
                },
                "row_id": {
                    "type": "long"
                }
            }
        }
    }
    try:
        # Create the index if not exists
        if not esConn.indices.exists(indexName):
            # Ignore 400 means to ignore "Index Already Exist" error.
            esConn.indices.create(
                index=indexName, body=indexBody  # ignore=[400, 404]
            )
            print("Created Index: ", indexName)
        else:
            print(f"Index {indexName} already exists")
    except Exception as ex:
        print(str(ex))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Load xml data into a ElasticSearch dense vector")
    parser.add_argument('--inputDir',  action="store", 
                        help= "Specify the dir containing the files to load")
    parser.add_argument('--indexName',  action="store", 
                        help ="The name of the index in to which to load the data")

    args = parser.parse_args()

    main(args)
