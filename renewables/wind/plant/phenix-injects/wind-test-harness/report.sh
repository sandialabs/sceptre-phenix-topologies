#!/bin/bash

# Scan test result files for times and results
for f in $(ls *_test.txt); do 
	RES=$(cat $f | grep 'TEST')
	F2=$(echo $f | sed -r 's/_test//g')
	TIME=$(cat $F2 | grep 'real' | sed -r 's/real\s+//g')
	echo -e "$f\t $TIME\t $RES"| column
done
