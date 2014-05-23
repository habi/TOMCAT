#! /bin/bash
# usage: missingSinoOff 
# start the script in the data folder where the samples of interest are
# Data10 for example and it will run on all folders with */*/tif without 
# a sin folder
# the nice command makes sure sinofly has priority when doing active
# measurements
sinoOffCmd="nice -n 19 python /work/sls/bin/sinooff_tomcat_j.py"
for curSample in */*/
do
	if [ -d "$curSample/tif" ]
	then
		outMsg="For Sample $curSample tif found checking for sino"
		echo "$outMsg"
		if [ -d "$curSample/sin" ]
		then
			outMsg="Sino Found, No Sinooff needed"
			echo "$outMsg"
		else
			echo "Launching Sinooff $curSample"
			soCmd="$sinoOffCmd $curSample/tif"
			$soCmd
		fi
	fi
done
