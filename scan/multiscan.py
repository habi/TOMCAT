""" Multiscan Viewer
# Kevin Mader (kevin.mader@gmail.com)
#
# Takes a given slice out of a folder of reconstructions and makes a folder filled with those images
# Input parameter is slice to take, a negative number takes slices every input slices between 0 and 3000 to make multiple
# In the sample directory run
#    python ~/beamline-scripts/postscan/multiscanViewer.py 1601

# To run for all samples
# for cdir in *; do cd $cdir; python ~/beamline-scripts/postscan/multiscanViewer.py 1200; cd ..; done
"""
from glob import glob
from PIL import Image
import os,sys
import numpy
sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/bin/"))
from X_ROBOT_X02DA_robotCommon import RoboEpicsChannel as EpicsChannel
from time import sleep

fileChannel=EpicsChannel("X02DA-SCAN-CAM1:FILPRE")
startChannel=EpicsChannel("X02DA-SCAN-SCN1:GO")


if len(sys.argv)<2: scanCount=5
else: scanCount=int(sys.argv[1])

if len(sys.argv)<3: sleepTime=0
else: sleepTime=int(sys.argv[2])

baseName=fileChannel.getVal()

if(startChannel.getVal()>0):
	print "Scan is currently running, please wait for it to finish..."
	exit(0)
	

def runScan(curScan,sleepAfterScan=0):
	fileChannel.putVal(baseName+"_%03d" % (curScan))
	print "Name has been set to:"+fileChannel.getVal()
	sleep(1)
	startChannel.putVal(1)
	print "Scan "+str(curScan)+" has been started"
	sleep(1)
	while (startChannel.getVal()>0): sleep(1)
	print "Scan completed, sleeping for: "+str(sleepAfterScan)+"s"
	sleep(sleepAfterScan)

for i in range(scanCount): runScan(i,sleepTime)

	

