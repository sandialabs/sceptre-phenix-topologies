# nmap scan

# put a list of "IP/SUBNET" to be nmap'ed
TARGETS=("192.168.100.0/24"\
	"#172.20.100.0/16"
	)

# 
for h in ${TARGETS[@]}; do
	# if first line starts with # skip that host
	if [[ "$h" =~ ^#.* ]]; then
		continue
	fi
	# quick scan should take about 20 per subnet
	nmap -Pn $h -p 1-100,502
done

