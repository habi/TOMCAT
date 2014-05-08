#!/usr/bin/python
'''
Multiscan Runner
 Kevin Mader (kevin.mader@gmail.com)

 To run 15 scans with a 10s delay between each scan execute the following command
  ! Note SPEC must already be running and waiting for the go channel to be set
    python ~/beamline-scripts/scan/multiscan.py 15 10

'''
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

	

