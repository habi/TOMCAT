# run from 1 to 10
# for i in $( seq 1 10 ); do ../makehdf5.cmd $i; done
# kill all reconstruction jobs qdel -u r14574

# important settings
darkCnt=20
flatCnt=80
projCnt=1501
reconSettings="-c 1280 -n -0.002 -x 0.003 -U 0.3 -t 16 -F parz -Z 0.5" 
# zinger = -z, zinger width = L

# load libraries and execute 

module use /opt/xbl-software/modulefiles-private
#and this is for mpi
module use /opt/xbl-software/modulefiles
#module avail
#echo $MODULEPATH
module load xbl/mpi
module load xbl/epd
module load xbl/tifffile/2012.01.01





# name of the current directory is assumed to be the sample name
preFix=${PWD##*/}
# tif directory
cDir=$(pwd)
tifDir="$cDir/tif"
flatStart=$((darkCnt+1))
scanNumber=$1
projIn=$((projCnt*(scanNumber-1)))
projStart=$((projIn+flatCnt+flatStart+1)) # first scan

echo "Making/Reconstruction $preFix $scanNumber, startproj:$projStart"

toolsDir="/afs/psi/project/TOMCAT_pipeline/Beamline/tomcat_pipeline/src/HDF5"
localConv="python $toolsDir/tif2hdf5.py"
sgeConv="$toolsDir/tif2hdf5_SGE.sh --ncores=2"

convCmd="$localConv" # comment out this line to run it on the cluster (can cause issues)

# reuse the same hdf5 file
hdfName="$preFix.hdf5"
# create a new one for each scan (better for loops)
hdfName="projs_${scanNumber}.hdf5"
baseArgs="-D $tifDir -P $preFix -z 4 $hdfName"


darkArgs="-d -s 1 -n $darkCnt"
flatArgs="-f -s $flatStart -n $flatCnt"
projArgs="-p -s $projStart -n $projCnt"

if ([ -a "$hdfName" ])
then
	echo "File $hdfName exists will just change projections"
else
	echo "Creating HDF5 with dark and flats"
	$convCmd $darkArgs $baseArgs
	$convCmd $flatArgs $baseArgs
fi
$convCmd $projArgs $baseArgs
prjLine="/afs/psi/project/TOMCAT_pipeline/Beamline/tomcat_pipeline/src/prj2sinSGE.sh"
sflatCnt=$((flatCnt/2))
sdarkCnt=$((darkCnt))
prjSettings="-f $projCnt,$sdarkCnt,$sflatCnt,0,0"
stdSge="$prjLine --ncores=60 --email=kevinmader+tomcatsge@gmail.com -R $scanNumber -I 2 -d"
dirSettings="-o $cDir/sino_${scanNumber}/ $hdfName"
prjCmd="$stdSge $prjSettings $reconSettings $dirSettings"
$prjCmd
