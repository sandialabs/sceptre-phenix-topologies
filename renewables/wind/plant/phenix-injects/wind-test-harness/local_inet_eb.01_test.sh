#!/bin/bash 

# A command to verify that this feature has produced expected output
# maybe a curl command to check an elk index or something of that sort
#diff example_golden_output.txt example1_feature1.txt
# for now we just test that the attack was successful 
# look for a win in the output 
REQFILE="ebsessiongood.var"

if [ ! -f $REQFILE ] 
then
	echo "TEST FAIL"
else
	echo "TEST PASS"
fi

# todo add this to a test to validate elastic is getting this string
#./elastic_search_helper.sh "remote"
#python3 elastic_verify.py "remote code"