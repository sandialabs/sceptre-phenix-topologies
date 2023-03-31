idxs=$(curl -X GET 'http://172.16.60.55:9200/_cat/indices' | grep $(date +%Y.%m.%d) | awk '{print $3}')
idxs+=("detections")
query='{"query":{"match_all":{}}}'
for idx in ${idxs[@]};
do 
	echo "Working $idx"
	curl -k -X POST --header 'Content-Type: application/json' "http://172.16.60.55:9200/${idx}/_delete_by_query" -d $query > $1/${idx}_$1.json;
done
curl -X GET 'http://172.16.60.55:9200/_cat/indices' | grep $(date +%Y.%m.%d)

