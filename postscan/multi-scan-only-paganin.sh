#!/bin/bash
# usage: multipleScanRename from_name to_name from_prefix  numberOfScans-1 
# example ~/macros/multipleScanRename.sh "dkmm01g80_" "dkmm01k" "dkmm01g" 99
# the flats and darks has to be at a separate directory named dkmm01g_flats with the prefix dkmm01g80_ and with the correct numbering. The log is changed as
#well.

#NumberOfScans=$2
#loopScans=NumberOfScans-1

for ((n=0; n <= $2; n++))
do  	
	if [ "$n" -lt "10" ]
	then	 
echo "Paganin pahse retrieval: "$1"0$n"; sinooff_tomcat_paganin.py "$1"0$n\_/tif/ 5.6E-07 2.2E-10 200 ;
	elif [ "$n" -lt "100" ] 
	then
echo "Paganin phase retrieval "$1"$n"; sinooff_tomcat_paganin.py "$1"$n\_/tif/ 5.6E-07 2.2E-10 200 ;
fi;
done

echo " copying and renaming finished"


#for n in {10..29} ; do echo "copying $n";cp dkmm01g_flats/* dkmm01k$n\_/tif/;
#echo "renaming";rename dkmm01k$n\_/tif/dkmm01g80_ dkmm01k$n\_/tif/dkmm01k$n\_ dkmm01k$n\_/tif/dkmm01g80_*;
#sed -i 's/01g/01k/g' dkmm01k$n\_/tif/dkmm01k$n\_.log; sed -i "s/01k80/01k$n/g" dkmm01k$n\_/tif/dkmm01k$n\_.log;  
#done
