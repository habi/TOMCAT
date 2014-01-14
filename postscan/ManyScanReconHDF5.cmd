
## run just job number 1 (for single scans)
# ~/beamline-scripts/postscan/ManyScanReconHDF5.cmd 1
## run scans from 1 to 10
# for i in $( seq 1 10 ); do  ~/beamline-scripts/postscan/ManyScanReconHDF5.cmd $i; done
## list all reconstruction jobs running: qstat
# qstat -xml | grep JB_name
## kill a single job 
# qdel (job-iD from qstat)
## kill all reconstruction jobs 
# qdel -u e14574
## prevent jobs (hold)  486385 to 486711 from running
# for i in `seq 486385 486711`; do qhold $i; done
## prevent all jobs for user e14574 in the queue currently from running
# qhold -u e14574
## release jobs to run 
# for i in `seq 486385 486711`; do qrls $i; done
## tell all jobs of user e14574 not to send mail
# qalter -m n -u e14574
## change the address for all jobs of user e14574
# qalter -M kevinmader+tomcatsge@gmail.com -u e14574


# important settings
darkCnt=20
flatCnt=80
projCnt=1501
# center, minimum, maximum value, parzen filter setting, 16 bit, filter, zero padding, cut projections (left, right, top, bottom)
reconSettings="-c 1280 -n -0.002 -x 0.003 -U 0.3 -t 16 -F parz -Z 0.5 -r 0,0,720,0" # 
ncores=12 # number of cores to use (if not cutting, full ROI, it should be 30, if cutting 700+ slices then 12)
# zinger = -z, zinger width = L
# wavelet -y db20 (db15-db20)
# -V 1-5 (larger number for larger rings)
# -E 2.0 (larger for larger rings)
# region of interest in image -e 1,720,2560,2160 x from 1 to 2560, y from 720 to 2160
# email to send job status to
email="kevinmader+tomcatsge@gmail.com"
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
stdSge="$prjLine --ncores=$ncores --email=$email --jobname=s${scanNumber}_${preFix} -R $scanNumber -I 2 -d"
dirSettings="-o $cDir/sino_${scanNumber}/ $hdfName"
prjCmd="$stdSge $prjSettings $reconSettings $dirSettings"
$prjCmd
