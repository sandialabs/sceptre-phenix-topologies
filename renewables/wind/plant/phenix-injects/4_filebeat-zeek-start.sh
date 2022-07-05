#!/bin/bash
filebeat setup -e
filebeat setup --index-management -E output.logstash.enabled=false -E 'output.elasticsearch.hosts=["192.168.0.254:9200"]'
filebeat export template > filebeat.template.json
curl -XPUT -H 'Content-Type: application/json' http://{{FIX_ME}}:9200/_template/filebeat-7.9.3 -d@filebeat.template.json
