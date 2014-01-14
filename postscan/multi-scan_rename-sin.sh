#!/bin/bash
# usage: multipleScanRename from_name to_name from_prefix  numberOfScans-1 delta beta z E ps
# example ~/macros/multipleScanRename.sh "dkmm01g80_" "dkmm01k" "dkmm01g" 99
# the flats and darks has to be at a separate directory named dkmm01g_flats with the prefix dkmm01g80_ and with the correct numbering. The log is changed as
#well.

#NumberOfScans=$2
#loopScans=NumberOfScans-1

for ((n=0; n <= $2; n++))
do  	
	if [ "$n" -lt "10" ]
	then	 
echo "copying and renaming  "$1"0$n";cp "$1"\_flats/* "$1"0$n\_/tif/ ; rename "$1"0$n\_/tif/"$1"0"$2" "$1"0$n\_/tif/"$1"0$n "$1"0$n\_/tif/"$1"0"$2"*; sed -i "s/"$1"0"$2"/"$1"0$n/g" "$1"0$n\_/tif/"$1"0$n\_.log; sinooff_tomcat_j.py "$1"0$n\_/tif/ ;

	elif [ "$n" -lt "100" ] 
	then
echo "copying and renaming  "$1"$n";cp "$1"\_flats/* "$1"$n\_/tif/ ; rename "$1"$n\_/tif/"$1""$2" "$1"$n\_/tif/"$1"$n "$1"$n\_/tif/"$1""$2"*; sed -i "s/"$1""$2"/"$1"$n/g" "$1"$n\_/tif/"$1"$n\_.log; sinooff_tomcat_j.py "$1"$n\_/tif/ ;
 
fi;
done

echo " copying and renaming finished"


#for n in {10..29} ; do echo "copying $n";cp dkmm01g_flats/* dkmm01k$n\_/tif/;
#echo "renaming";rename dkmm01k$n\_/tif/dkmm01g80_ dkmm01k$n\_/tif/dkmm01k$n\_ dkmm01k$n\_/tif/dkmm01g80_*;
#sed -i 's/01g/01k/g' dkmm01k$n\_/tif/dkmm01k$n\_.log; sed -i "s/01k80/01k$n/g" dkmm01k$n\_/tif/dkmm01k$n\_.log;  
#done
