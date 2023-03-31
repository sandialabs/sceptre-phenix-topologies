#!/bin/bash

OLD=$(ls -lth *.txt | head -n 1)
while [ 1 ]; do 
	NEW=$(ls -lth *.txt | head -n 1)
	if [ "$OLD" != "$NEW" ]; then 
		tail $(ls -t *.txt | head -n 1);
		OLD=$(ls -lth *.txt | head -n 1)
	fi
	sleep 1;
done

