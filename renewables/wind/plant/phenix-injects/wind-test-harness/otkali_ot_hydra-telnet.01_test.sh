#!/bin/bash 

# A command to verify that this feature has produced expected output
# maybe a curl command to check an elk index or something of that sort

# first arg is the 'new' file, results of the test
# second arg is the name of the golden file to compare

# lets make sure the results exist, this may not apply to all cases
if [ ! -f $1 ]; then
	echo "TEST FAIL"
	exit 1
fi
	

# get number of passwords found
NUMCHECK=$(cat $1 | grep -i '1 valid password found' | wc -l)
# ensure greater than 0
test $NUMCHECK -gt 0

# if test returns 0 good, else fail
if [ $? -eq 0 ]; then
	echo "TEST PASS"
	exit 0
else # if grep returns err=0 then it DID find 'failed'
	echo "TEST FAIL"
	exit 1
fi

