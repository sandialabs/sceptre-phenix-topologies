for i in $(seq 0 $1); do rm *.txt; ./main.sh; echo -e "\n$(date)" >> report.all; ./report.sh >> report.all; done
