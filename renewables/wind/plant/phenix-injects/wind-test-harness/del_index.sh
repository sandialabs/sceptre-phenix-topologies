# Script to wipe ElasticSearch tests index so we only have test results after running the experiment

# Dont ever do _all unless you want to wipe all the indicies
# curl -X DELETE 'http://172.16.60.55:9200/_all'

URL="http://172.16.60.55:9200/tests-$(date '+%Y-%m-%d')"
curl -X DELETE 'http://172.16.60.55:9200/tests-*'
curl -X PUT $URL # recreate so there is a index to read
