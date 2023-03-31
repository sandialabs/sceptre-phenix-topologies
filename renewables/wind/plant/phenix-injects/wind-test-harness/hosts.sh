#!/bin/bash
send_keys(){
	OLDIFS=$IFS
	IFS=";"
	while read host un ip
		do
			if [[ "$host" =~ ^#.* ]]; then
				continue
			fi
			echo $host
			ssh-copy-id -i ./thkey.pub $un@$ip
	done < "./hosts.csv"
	IFS=$OLDIFS
}

send_file(){
	OLDIFS=$IFS
	IFS=";"
	while read host un ip
		do
			if [[ "$host" =~ ^#.* ]]; then
				continue
			fi
			echo $host
			IP=$(./hosts.sh ${host})
			UN=$(./hosts.sh ${host} un)
			PW=$(./hosts.sh ${host} pw)
			sshpass -p ${PW} scp -o StrictHostKeyChecking=no $1 $UN@${IP}:/tmp/
	done < "./hosts.csv"
	IFS=$OLDIFS
}

send_cmd(){
	OLDIFS=$IFS
	IFS=";"
	while read host un ip
		do
			if [[ "$host" =~ ^#.* ]]; then
				continue
			fi
			echo $host : $1
			IP=$(./hosts.sh ${host})
			UN=$(./hosts.sh ${host} un)
			PW=$(./hosts.sh ${host} pw)
			OUT=$(sshpass -p ${PW} ssh -n -o StrictHostKeyChecking=no $UN@${IP} -C $1)
			echo $OUT
	done < "./hosts.csv"
	IFS=$OLDIFS
}



get_ip(){
	OLDIFS=$IFS
	IFS=";"
	while read host un pw ip
		do

			if [[ "$host" =~ ^#.* ]]; then
				continue
			fi
			#echo $host
			if [ "$1" == "$host" ]
			then	
				if [ "$2" == "un" ]; then
					echo $un
					exit 0
				elif [ "$2" == "pw" ]; then
					echo $pw
					exit 0
				else
					echo $ip
					exit 0
				fi
			fi
	done < "./hosts.csv"
	echo "Not Found"
	exit 1
	IFS=$OLDIFS
}

if [ "$1" == "keys" ]; then
	send_keys
elif [ "$1" == "send" ]; then
	send_file $2
elif [ "$1" == "cmd" ]; then
	send_cmd "$2"
else
	get_ip $1 $2
fi
