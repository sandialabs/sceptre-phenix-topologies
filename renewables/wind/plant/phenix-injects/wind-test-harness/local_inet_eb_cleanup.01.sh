#!/bin/bash
REQFILE="ebsessiongood.var"

# if there is a msf session, remove what we did
if [ -f $REQFILE ]
then

msfrpc -a 127.0.0.1 -P letmein <<EOF
irb_context.echo = false
rpc.call('session.meterpreter_script', 1, 'wind_cleanup')
sleep 2
data = rpc.call('session.meterpreter_read', 1)
puts data
exit
EOF

fi

# kill the msfrpcd daemon 
pkill -f msfrpcd
# disc from vpn
wg-quick down wg0
# remove the file 
rm $REQFILE
