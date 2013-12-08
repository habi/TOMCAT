#!/bin/bash
# this script submits for reconstruction a scan series
# usage:multi_reco.sh <scan name> <number of scans -1> <rot. center> <level min> <level max> 
# example: 
#
#NumberOfScans=$2


for ((n=0; n <= $2; n++))
do  	
	if [ "$n" -lt "10" ]
	then	 
echo "submitting scan $1$n";~/www/reco/cvs/Python/tif2rec_batch_interface.py 7 30,1 "$1"0$n\_/tif/ "$3" 4,0,0.5 0 1 0,0,0,0 0,0,0 1,0.95,9 2,"$4","$5",0.0 0.5 "" 1,0,0 1; sleep 30;
	elif [ "$n" -lt "100" ] 
	then
echo "submitting scan $1$n";~/www/reco/cvs/Python/tif2rec_batch_interface.py 7 30,1 "$1"$n\_/tif/ "$3" 4,0,0.5 0 1 0,0,0,0 0,0,0 1,0.95,9 2,"$4","$5",0.0 0.5 "" 1,0,0 1; sleep 30;
fi;
done

echo " all submitted"
