#!/bin/bash

# this script will poll the elastic database and trigger playbooks via webhook when new 'interesting' messages come in

# start off with an initial count of alerts
# we could make this pull the alerts rn when script starts to avoid an initial trigger of playbook
LS_LASTCNT=0
WZ_LASTCNT=0

#startup
INDICES=$(curl -s -X GET 127.0.0.1:9200/_cat/indices?pretty)
echo $INDICES | grep logstash-$(date +%Y.%m.%d)
if [ $? != 0 ]; then
	echo "DID NOT FIND A LOGSTASH INDEX FOR TODAY, creating one"
	curl -X PUT 127.0.0.1:9200/logstash-$(date +%Y.%m.%d)
fi
echo $INDICES | grep wazuh-alerts-3.x-$(date +%Y.%m.%d)
if [ $? != 0 ]; then
	echo "DID NOT FIND A WAZUH ALERTS INDEX FOR TODAY, creating one"
	curl -X PUT 127.0.0.1:9200/wazuh-alerts-3.x-$(date +%Y.%m.%d)
fi

LS_QUERY='{"query": {"match": {"message": {"query": "Eternal"}}}}'
LS_QUERY='{"query": {"bool": {"must": [{"match": {"message": "Eternal Blue"}}]}}}'
WZ_QUERY='{"query": {"bool": {"must": [{"match": {"data.win.system.severityValue": "AUDIT_FAILURE"}}, {"match": {"data.win.eventdata.workstationName": "kali-ot"}}], "filter": [{"range": {"rule.level": {"gte": 5}}}]}}}'

# if we dont want it to fire every start, but only after new alerts
#LS_LASTCNT=$(curl -s -X GET 127.0.0.1:9200/logstash-$(date +%Y.%m.%d)/_search?pretty=true | grep -i message | wc -l)
#WZ_LASTCNT=$(curl -s -X GET 127.0.0.1:9200/wazuh-alerts-3.x-$(date +%Y.%m.%d)/_search?pretty=true | grep -i description | wc -l)
LS_LASTCNT=$(curl -s -X POST -H "Content-Type: application/json" 127.0.0.1:9200/logstash-$(date +%Y.%m.%d)/_count -d "$LS_QUERY"         | cut -d',' -f1 | cut -d':' -f2)
WZ_LASTCNT=$(curl -s -X POST -H "Content-Type: application/json" 127.0.0.1:9200/wazuh-alerts-3.x-$(date +%Y.%m.%d)/_count -d "$WZ_QUERY" | cut -d',' -f1 | cut -d':' -f2)

while [ 1 ]; do 
	#look for nozomi alertl
	#NOWCNT=$(curl -s -X GET 127.0.0.1:9200/logstash-2022.07.08/_search?pretty=true | grep -i message | wc -l)
	#NOWCNT=$(curl -s -X GET 127.0.0.1:9200/logstash-$(date +%Y.%m.%d)/_search?pretty=true | grep -i message | wc -l)
	NOWCNT=$(curl -s -X POST -H "Content-Type: application/json" 127.0.0.1:9200/logstash-$(date +%Y.%m.%d)/_count -d "$LS_QUERY" | cut -d',' -f1 | cut -d':' -f2)
	if [ $NOWCNT -eq $LS_LASTCNT ]; then
		echo " no new nozomi alerts $NOWCNT -eq $LS_LASTCNT"
	else
		LS_LASTCNT=$NOWCNT
		echo " new nozomi alerts calling playbook $NOWCNT -eq $LS_LASTCNT"
		# todo call hook here
		# curl PB1_HOOK
		curl -X POST http://172.16.60.50:9999 -H "Content-Type: application/json" -d '{"name":"EB_'${LS_LASTCNT}'"}'
	fi

	#look for wazuh alerts
	#NOWCNT=$(curl -s -X GET 127.0.0.1:9200/wazuh-alerts-3.x-2022.07.08/_search?pretty=true | grep -i description | wc -l)
	#NOWCNT=$(curl -s -X GET 127.0.0.1:9200/wazuh-alerts-3.x-$(date +%Y.%m.%d)/_search?pretty=true | grep -i description | wc -l)
	NOWCNT=$(curl -s -X POST -H "Content-Type: application/json" 127.0.0.1:9200/wazuh-alerts-3.x-$(date +%Y.%m.%d)/_count -d "$WZ_QUERY" | cut -d',' -f1 | cut -d':' -f2)
	if [ $NOWCNT -eq $WZ_LASTCNT ]; then
		echo " no new wazuh alerts $NOWCNT -eq $WZ_LASTCNT"
	else
		WZ_LASTCNT=$NOWCNT
		echo " new wazuh alerts calling playbook $NOWCNT -eq $WZ_LASTCNT"
		# todo call hook here
		# curl PB2_HOOK
		curl -X POST http://172.16.60.50:9998 -H "Content-Type: application/json" -d '{"name":"OT_'${WZ_LASTCNT}'"}'
	fi

	sleep 2
done

