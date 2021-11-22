# dug-dense-vectors
This directory contains 2 python codes. These are loadDenseVectors.py and dugSearchApp.py

Preconditions: ElasticSearch has to be running

Configuration is in the file config.py.  

loadDenseVectors.py:
This code creates connects to an ElasticSearch instance and creates an index specified with the indexName parameter.  It then reads file in the directory tree specified by the inputDir parameter and extracts information. Currently the files have to be XML files that contain fields that are hard-coded in this code, but that restriction will eventually have to be lifted.  The information is as an input to the Biobert sentence embedding module and the resulting vector is passed as part of the input that creates documents in the index. See 

  https://blog.accubits.com/vector-similarity-search-using-elasticsearch/

 for some insight into this process.

An example usage:

python createDugIndex.py --inputDir /projects/neurobridges/howard/dug-data --indexName dug1

reads the dbgap data dictionary files from /projects/neurobridges/howard/dug-data and loads a dense vector for each entry into the dug1 index of elasticSearch

dugSearchApp.py

This code starts a flask app that runs on port 5000 on the local host.  This app accepts requests that include a search string, creates a dense vector from the input query and sends it to ElasticSearch for a cosine query. The elastic ip hostname, port, index and search threshold are defined in config.py.

To start this server type:

python dugSearchApp.py

An example query to a search app running on host "testhost.edc.renci.org" to find items related to high blood pressure is:

curl -X Get  http://testhost.edc.renci.org:5000/query?query="high%20blood%20pressure" 
