# Wind_Data_Final_draft00

## The Indexes

Data from elastic search was scraped from the elasticsearch server shorltly after the attacks completed and stored as json files. The attacks on average took about 5 minutes to completed
and the data was scraped from elastic for a time period of 10 hours, so in most cases the data in the indexes were captured for a few minutes before the attack, the attack and a few 
minutes after. Baseline data was also collected and stored in the baseline folder, this data was a scrape of the elastic indexes before running any attacks to show what 'normal' data looks like. 
The query used to collect the data was as follows.  

query='{"query":{"range":{"@timestamp":{"gte":"now-10h","lt":"now"}}},"size":10000}'  

Between each suite of attacks the indexes are truncated (all data is erased). This way the data should not overlap between datasets. 

### detections index

The detections index is filled from a python script running on the pwds vm. The python script parses the bennu/power data and uses that to fill the physical metric. For example when 
the INET suite of attacks was ran against environment 1 the resulting physical + resilience score was 56 (see metric_inet_1.png) this score in the grafana dashboard was pulled from this 
index using the doc "Id" : "Score", "Detection" : 54.63. So the data used for the physical + resilience score on the grafana dashboard is pulled from this index.

### tests index

The tests index includes the start, stop and result of attacks ran via the test harness ATTAR. This will show when the attack started and what the result is for cross reference of the attack with the hids and nids output in the other indexes. Not all attacks have an 'output' entry, only attacks that were used in the metrics have the 'output' feild. Most docs in this index include the attack name, the stage and the @timestamp.

An Example:
		  "attack" : true,
          "name" : "inet-eb_modbus_attack.05",
          "stage" : "start"


### wazuh-alerts-3.x index

This index holds data from the wazuh ossec HIDS agents running in the ws-ot vm and the jh (jump host) vm. On ws-ot this agent is mostly just the windows event log. This index is mostly 
responsive to the brute force attacks that are run in the OT suite of attacks. The interesting data feild in this index is the "message" feild. 

For example:
"message" : "\"An account failed to log on.\r\n\r\nSubject:\r\n\tSecurity ID:\t\tS-1-0-0\r\n\tAccount Name:\t\t-\r\n\tAccount Domain:\t\t-\r\n\tLogon ID:\t\t0x0\r\n\r\nLogon Type:\t\t\t3\r\n\r\nAccount For Which Logon Failed:\r\n\tSecurity ID:\t\tS-1-0-0\r\n\tAccount Name:\t\t\r\n\tAccount Domain:\t\t\r\n\r\nFailure Information:\r\n\tFailure Reason:\t\tUnknown user name or bad password.\r\n\tStatus:\t\t\t0xc000006d\r\n\tSub Status:\t\t0xc0000064\r\n\r\nProcess Information:\r\n\tCaller Process ID:\t0x0\r\n\tCaller Process Name:\t-\r\n\r\nNetwork Information:\r\n\tWorkstation Name:\tLp40MMVRhDjGLkxn\r\n\tSource Network Address:\t10.222.222.45\r\n\tSource Port:\t\t32921\r\n\r\nDetailed Authentication Information:\r\n\tLogon Process:\t\tNtLmSsp \r\n\tAuthentication Package:\tNTLM\r\n\tTransited Services:\t-\r\n\tPackage Name (NTLM only):\t-\r\n\tKey Length:\t\t0\r\n\r\nThis event is generated when a logon request fails. It is generated on the computer where access was attempted.\r\n\r\nThe Subject fields indicate the account on the local system which requested the logon. This is most commonly a service such as the Server service, or a local process such as Winlogon.exe or Services.exe.\r\n\r\nThe Logon Type field indicates the kind of logon that was requested. The most common types are 2 (interactive) and 3 (network).\r\n\r\nThe Process Information fields indicate which account and process on the system requested the logon.\r\n\r\nThe Network Information fields indicate where a remote logon request originated. Workstation name is not always available and may be left blank in some cases.\r\n\r\nThe authentication information fields provide detailed information about this specific logon request.\r\n\t- Transited services indicate which intermediate services have participated in this logon request.\r\n\t- Package name indicates which sub-protocol was used among the NTLM protocols.\r\n\t- Key length indicates the length of the generated session key. This will be 0 if no session key was requested.\"",

### wazuh-monitoring-3.x index  

This index is just for internal wazuh data and is not used 

### logstash index

This index represents the nozomi NIDS data. This data is used by the orchestration to know when there is a targeted network attack on the network, specifically the orchestration is looking for an eternal blue attack. The interesting feild in this index is the "message" feild. It is named logstash and not NIDS or nozomi because the data goes from nozomi to a logstash server (another vm named logstash) and then forwarded to elastic.

For example:
"message" : "A suspicious packet was sent [sid:41978] -- Microsoft Windows SMB remote code execution attempt. Activity was detected related to an exploit at the SMB protocol - Eternal Blue. The SMBv1 server in Microsoft Windows Vista SP2, Windows Server 2008 SP2 and R2 SP1, Windows 7 SP1, Windows 8.1, Windows Server 2012 Gold and R2, Windows RT 8.1, and Windows 10 Gold, 1511, and 1607, and Windows Server 2016 allows remote attackers to execute arbitrary code via crafted packets.",

### bennu index

The bennu index contains the raw power data. Even though the index might be as large as 32mb it only contains about 1200 unique values, and most of them are unique because of small 
differences in very small parts of the decimal numbers. The data is collected at a very fast rate so there is a lot of repeat data and the json file can be large. Since the data is so 
large in most cases the data might not go back the full 30 minutes as the amount of data that can be pulled is normally capped at 10,000 records. In some cases the cap was extended to 
500,000 records and will cover a larger time period. 

The relative fields of this index are 
          "field" : "active",
          "field" : "base_kv",
          "field" : "bus",
          "field" : "current",
          "field" : "freq",
          "field" : "mva_base",
          "field" : "mvar",
          "field" : "mw",
          "field" : "mw_max",
          "field" : "mw_min",
          "field" : "voltage",
          "field" : "voltage_angle",
          "field" : "voltage_setpoint",

These fields are for 30 different generation assets 
		  "device" : "generator-10_bus-2100",
          "device" : "generator-11_bus-2100",
          "device" : "generator-12_bus-2100",
          "device" : "generator-13_bus-2100",
          "device" : "generator-14_bus-2100",
          "device" : "generator-15_bus-2100",
          "device" : "generator-16_bus-2100",
          "device" : "generator-17_bus-2100",
          "device" : "generator-18_bus-2100",
          "device" : "generator-19_bus-2100",
          "device" : "generator-1_bus-2100",
          "device" : "generator-20_bus-2100",
          "device" : "generator-21_bus-2100",
          "device" : "generator-22_bus-2100",
          "device" : "generator-23_bus-2100",
          "device" : "generator-24_bus-2100",
          "device" : "generator-25_bus-2100",
          "device" : "generator-26_bus-2100",
          "device" : "generator-27_bus-2100",
          "device" : "generator-28_bus-2100",
          "device" : "generator-29_bus-2100",
          "device" : "generator-2_bus-2100",
          "device" : "generator-30_bus-2100",
          "device" : "generator-3_bus-2100",
          "device" : "generator-4_bus-2100",
          "device" : "generator-5_bus-2100",
          "device" : "generator-6_bus-2100",
          "device" : "generator-7_bus-2100",
          "device" : "generator-8_bus-2100",
          "device" : "generator-9_bus-2100",




## Sequence of events  
Here is a log of the actions performed to collect the data. The capital names represent the directory where the data is stored.  
For example INET_1 was the INET suite of attacks ran against environment 1.

### Environment 1

- truncated the indexes, allowed kali-inet from vyatta vnc
- disabled pbtrigger, restarted ws-ot (it was not working with eb)
d INET_1 - ran ./main.sh inet
- trucated the indexes
e OT_1 - ran ./main.sh ot

### Environment 2

- truncated indexes, started ws-ot
ran ./main.sh inet
INET_2 ran ./get_es_data.sh after_exp2_a
- truncated indexes
ran ./main.sh ot
OT_2 ran ./get_es_data.sh after_exp2_b

### Environment 4

- truncated indexes
ran ./main.sh inet
INET_4 ran ./get_es_data.sh after_exp4_a
- truncated indexes
ran ./main.sh ot
OT_4 ran ./get_es_data.sh after_exp4_b

### Environment 5

a INET_5 - ran ./main.sh inet, 
- truncated the indexes, allowed kali-inet from vyatta vnc
b OT_5 - ran ./main.sh ot
- truncated the indexes, allowed kali-ot from compute2
c INET_5 - ran ./main.sh inet 

### Additional  

During the creation of the dataset it was required to go back and re run several several times. For instance in the environment 5 the tests were ran 5x each on the environment to establish a average reaction time of the SOAR component. As the tests were ran again and again and new datasets were added to the data the team found better ways to capture more of the data. So, in general datasets captured later will be fuller than earlier datasets. The latter datasets will include a main.sh.***.log file which includes the times and output of the main.sh test harness script, this log shows how each test ran, how long it took and so on. Also in the later datasets all of the log data for each attack was captured for the attacks in the testharness folder as .txt files. In the testharness folders you can run the ./report.sh script to get a report of the test results. The baseline and environments 3 and 5 both have updated and more filled out datasets.
