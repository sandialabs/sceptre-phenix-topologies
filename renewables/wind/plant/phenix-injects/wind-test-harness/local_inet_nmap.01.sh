# nmap scan

# only firewall rules to reach windows machine
nmap 192.168.100.100
#nc -z 192.168.100.100 3389
#if [ $? -eq 0 ]; then
#	echo "found 3389 open"
#fi

# pass: 3389
