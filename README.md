# dug-dense-vectors
This code creates connects to an ElasticSearch instance and creates an index specified with the indexName parameter.  It then reads file in the directory tree specified by the inputDir parameter and extracts information. Currently the files have to be XML files that contain fields that are hard-coded in this code, but that restriction will eventually have to be lifted.  The information is as an input to the Biobert sentence embedding module and the resulting vector is passed as part of the input that creates documents in the index. See 

  https://blog.accubits.com/vector-similarity-search-using-elasticsearch/

 for some insight into this process.
