# Script to save off ElasticSearch data from the experiment

# expand to 500k docs we can pull per index
curl -k -X PUT --header 'Content-Type: application/json' "http://172.16.60.55:9200/_settings" -d '{ "index.max_result_window": 500000 }'

# get the indeses we want
idxs=$(curl -X GET 'http://172.16.60.55:9200/_cat/indices' | grep $(date +%Y.%m.%d) | awk '{print $3}')
idxs+=("detections")
# set the query to max 500k and 10h from now
query='{"query":{"range":{"@timestamp":{"gte":"now-10h","lt":"now"}}},"size":500000}'
mkdir ~/$1
mkdir ~/$1/th
for idx in ${idxs[@]};
do 
	echo "Working $idx"
	curl -k -X GET --header 'Content-Type: application/json' "http://172.16.60.55:9200/${idx}/_search?pretty" -d $query > ~/$1/${idx}_$1.json;
done

curl -k -X GET --header 'Content-Type: application/json' "http://172.16.60.55:9200/xsoar/_search?pretty" -d $query > ~/$1/xsoar_$1.json;
# copy over all tests and results 
cp ./* ~/$1/th/
tar -zcvf ~/$1.tgz ~/$1

# note you can run this to get more results
# PUT _settings { "index.max_result_window": 500000 }
# curl -k -X PUT --header Content-Type: application/json http://172.16.60.55:9200/_settings -d { "index.max_result_window": 500000 }
