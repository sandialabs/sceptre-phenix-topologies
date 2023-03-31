#!/bin/bash 

# copy custom cmd code for the attack
cp wind_add_user.rb /usr/share/metasploit-framework/scripts/meterpreter/wind_add_user.rb
cp wind_schtask.rb /usr/share/metasploit-framework/scripts/meterpreter/wind_schtask.rb
cp wind_cleanup.rb /usr/share/metasploit-framework/scripts/meterpreter/wind_cleanup.rb

# Set up the VPN
wg-quick up wg0

echo "Starting MSF RPC daemon..."
msfrpcd -a 127.0.0.1 -P letmein
ping -c 2 192.168.100.100
