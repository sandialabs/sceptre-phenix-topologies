#!/bin/bash 

# A command to verify that this feature has produced expected output
# maybe a curl command to check an elk index or something of that sort
#diff example_golden_output.txt example1_feature1.txt
# for now we just test that the attack was successful 
# look for a win in the output 
# use this first line if expecting 'True'
NUMSUC=$(cat ./$1 | grep "Success? True and True" | wc -l)
#NUMSUC=$(cat ./$1 | grep "Success?" | wc -l)
if [ $NUMSUC -gt 2 ]; then
	echo "TEST PASS"
else
	echo "TEST FAIL"
fi

# todo add this to a test to validate elastic is getting this string
#./elastic_search_helper.sh "remote"
#python3 elastic_verify.py "remote code"
