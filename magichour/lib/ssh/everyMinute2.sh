#!/bin/bash

while :
do
		echo "running"
	  python ./sshSessionGen.py -c ./commands -d 10 -a $1 -s 300 -l $2	&
		sleep 60 
done