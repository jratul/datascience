#! /bin/ksh

if [ $1 = "1" ]; then
	python clustering.py input1.txt 8 15 22
elif [ $1 = "2" ]; then
	python clustering.py input2.txt 5 2 7
elif [ $1 = "3" ]; then
	python clustering.py input3.txt 4 5 5
else
	echo "input parameter"
fi



