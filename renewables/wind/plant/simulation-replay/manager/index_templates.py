#file: index_templates.py
#auth: rafer cooley
#desc: only contains index template mappings to be uploaded by manager into elasticsearch

from variables import *

BENNU_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["bennu-*"],
    "template":{
        "mappings":{
            "properties": {
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                "provider": {"type":"text"},
                "device": {"type":"text"},
                "field": {"type":"text"},
                "status": {"type":"text"},#TODO: validate this shouldn't be a boolean
                "value": {"type":"float"},
            }
        },
        "aliases":{
            "bennu": {}
        }
    }
}

DETECTIONS_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["detections*"],
    "template":{
        "mappings":{
            "properties": {
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                "_doc": {
                    "properties": {
                        "Id": {"type":"text"},
                        "Detection":{"type":"float"}
                    }
                }
            }
        },
        # "aliases":{
        #     "detections":{} #NOTE: removed this alias field b/c elasticsearch errors when index-patterns==aliases. Doesn't matter much since this index doesn't use the date in its name like the others
        # }
    }
}
#structure as defined in resilience_metric-v4.py
# detections_index_structure = {
# 	"mappings": {
# 		"properties": {
# 			"Id": {
# 				"type": "text",
# 				"fields": {
# 					"keyword": {
# 						"type": "keyword"
# 					}
# 				}
# 			},
# 			"@timestamp": {
# 				"type": "date",
# 				"format": "yyy-MM-dd HH:mm:ss" <<-- TODO: error in year definition here, doesn't seem to be present in data files
# 			},
# 			"Detection": {
# 				"type": "float"
# 			}
# 		}
# 	}
# }

TESTS_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["tests-*"],
    "template":{
        "mappings":{
            "properties": {
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                "attack": {"type":"boolean"},
                "name": {"type":"text"},
                "stage": {"type":"text"},
                "output": {"type":"text"},
            }
        },
        "aliases":{
            "tests":{}
        }
    }
}#timestamp,attack(bool),name(str),stage(str),output(str)

LOGSTASH_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["logstash-*"],
    "template":{
        "mappings":{
            "properties": {
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                "deviceCustomString5": {"type":"text"},
                "name": {"type":"text"},
                "severity": {"type":"float"},
                "flexString1Label": {"type":"text"},
                "deviceVendor": {"type":"text"},
                "deviceCustomString6": {"type":"text"},
                "deviceCustomString2Label": {"type":"text"},
                "flexString3Label": {"type":"text"},
                "cefVersion": {"type":"text"},
                "deviceCustomString3": {"type":"text"},
                "deviceProduct": {"type":"text"},
                "deviceCustomString5Label" : {"type":"text"},
                "deviceAddress": {"type":"text"},
                "deviceCustomString3Label": {"type":"text"},
                "transportProtocol": {"type":"text"},
                "deviceCustomString6Label": {"type":"text"},
                "startTime": {"type":"text"},
                "deviceHostName": {"type":"text"},
                "flexString3": {"type":"text"},
                "host": {"type":"text"},
                "sourceAddress": {"type":"text"},
                "flexString2Label": {"type":"text"},
                "deviceCustomString1Label": {"type":"text"},
                "deviceVersion": {"type":"text"},
                "flexString1": {"type":"text"},
                "sourcePort": {"type":"integer"},
                "port": {"type":"integer"},
                "flexString2": {"type":"text"},
                "syslog": {"type":"text"},
                "sourceMacAddress": {"type":"text"},
                "deviceEventClassId": {"type":"text"},
                "deviceCustomString2": {"type":"text"},
                "deviceCustomString1": {"type":"text"},
            }
        },
        "aliases":{
            "logstash":{}
        }
    }
}

WAZUH_ALERTS_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["wazuh-alerts-3.x-*"],
    "template":{
        "mappings":{
            "properties": {
                # "@timestamp": {"type":"date","format":"yyyy-MM-dd HH:mm:ss"},
                # "@timestamp": {"type":"date","format":"yyyy-MM-ddTHH:mm:ss:SSSSS"},
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                # "timestamp" : {"type":"date","format":"yyyy-MM-ddTHH:mm:ss.SSSSS"},#NOTE: both are required!
                "timestamp" : {"type":"date","format":"strict_date_optional_time_nanos"},#NOTE: both are required!
                "location" : {"type":"text"},
                "id" : {"type":"text"},
                "agent" : {
                    "properties": {
                        "ip" : {"type":"text"},
                        "name" : {"type":"text"},
                        "id" : {"type":"text"},
                    }
                },
                "manager" : {
                    "properties": {
                        "name" : {"type":"text"},
                    }
                },
                "data" : {
                    "properties": {
                        "win" : {
                            "properties": {
                                "eventdata" : {
                                    "properties": {
                                        "subjectLogonId" : {"type":"text"},
                                        "authenticationPackageName" : {"type":"text"},
                                        "workstationName" : {"type":"text"},
                                        "subStatus" : {"type":"text"},
                                        "logonProcessName" : {"type":"text"},
                                        "targetUserName" : {"type":"text"},
                                        "keyLength" : {"type":"text"},
                                        "subjectUserSid" : {"type":"text"},
                                        "processId" : {"type":"text"},
                                        "failureReason" : {"type":"text"},
                                        "targetUserSid" : {"type":"text"},
                                        "logonType" : {"type":"text"},
                                        "status" : {"type":"text"},
                                    }
                                },
                                "system" : {
                                    "properties": {
                                            "eventID" : {"type":"text"},
                                            "keywords" : {"type":"text"},
                                            "providerGuid" : {"type":"text"},
                                            "level" : {"type":"text"},
                                            "channel" : {"type":"text"},
                                            "opcode" : {"type":"text"},
                                            "message" : {"type":"text"},
                                            "version" : {"type":"text"},
                                            "systemTime" : {"type":"text"},
                                            "eventRecordID" : {"type":"text"},
                                            "threadID" : {"type":"text"},
                                            "computer" : {"type":"text"},
                                            "task" : {"type":"text"},
                                            "processID" : {"type":"text"},
                                            "severityValue" : {"type":"text"},
                                            "providerName" : {"type":"text"},
                                    }
                                }
                            }
                        }
                    }
                },
                "rule" : {
                    "properties": {
                        "firedtimes" : {"type":"integer"},
                        "mail" : {"type":"boolean"},
                        "level" : {"type":"integer"},
                        "pci_dss" : {"type":"text"},#array
                        "hipaa" : {"type":"text"},#array
                        "tsc" :  {"type":"text"},#array
                        "description" :  {"type":"text"},
                        "groups" : {"type":"text"},#array
                        "id" : {"type":"text"},
                        "nist_800_53" : {"type":"text"},#array
                        "gpg13" : {"type":"text"},#array
                        "gdpr" : {"type":"text"},#array
                    }
                },
                "decoder" : {
                    "properties": {
                        "name" : {"type":"text"},
                    }
                },
                "input" : {
                    "properties": {
                        "type" : {"type":"text"},
                    }
                }
            }
        },
        "aliases":{
            "wazuh-alerts-3.x": {}
        }
    }
}

WAZUH_MONITORING_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["wazuh-monitoring-3.x-*"],
    "template":{
        "mappings":{
            "properties": {
                # "@timestamp": {"type":"date","format":"yyyy-MM-dd HH:mm:ss"},
                # "@timestamp": {"type":"date","format":"yyyy-MM-ddTHH:mm:ss:SSSSS"},
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                "TODO": {"type":"text"}
            }
        },
        "aliases":{
            "wazuh-monitoring-3.x":{}
        }
    }
}

XSOAR_ENVS_INDEX_TEMPLATE = {
    "version": 1,
    "index_patterns":["xsoar-*"],
    "template":{
        "mappings":{
            "properties": {
                # "@timestamp": {"type":"date","format":"yyyy-MM-dd HH:mm:ss"},
                # "@timestamp": {"type":"date","format":"yyyy-MM-ddTHH:mm:ss:SSSSSZ"},
                "@timestamp": {"type":"date","format":MASTER_OUTPUT_ELASTICSEARCH_DATE_FORMAT_STRING},
                "msg": {"type":"text"}
            }
        },
        "aliases":{
            "xsoar":{}
        }
    }
}
