#! /usr/bin/env python
# NOTE this is only a template and thus may contain inconsistencies and errors

import sys
import os.path
import string
import commands
import math
#---------------------------------------------------------------------------
                          #---------------------------------
                          #----------------------------------------------
                          # Make sure we are running at least python level 2.
                          # CaChannel seems to give troubles otherwise!
if sys.version[0:1] == "1":
  python2 = commands.getoutput ("type -p python2")
  if python2 == "":
    print "\n\aThe default python version is", sys.version
    print     "and this script needs python level 2 or higher."
    print     " Python level 2 cannot be found."
    os.system ("xkbbell")
    os.system ("xmessage -nearmouse -timeout 30 -buttons '' Python level 2 cannot be found")
    sys.exit (1)
  #endif
  sys.argv.insert (0, python2)
  os.execv (python2, sys.argv)
#endif
if sys.version[0:1] == "1":
  print "\n\aThe loading of a higher level of python seems to have failed!"
  sys.exit (1)
#endif
#---------------------------------------------------------------------------
try:
  from CaChannel import *
except:
  #try:
  #  sys.path.insert (0, os.path.expandvars ("$SLSBASE/sls/lib/python22/CaChannel"))
  #  from CaChannel import *
  #except:
  os.system ("xkbbell")
  os.system ("xmessage -nearmouse -timeout 30 -buttons '' CaChannel module cannot be found")
  sys.exit (1)
  #endtry
#endtry

from CaChannel import CaChannelException

#---------------------------------------------------------------------------

class EpicsChannel:
    def __init__(self,pvName):
        self.pvName=pvName
        try:
            self.chan=CaChannel()
            self.chan.search(self.pvName)
            self.chan.pend_io()
            self.connected=1
        except CaChannelException, status:
            print ca.message(status)
            self.connected=0

    def getVal(self):
        try:
                val=self.chan.getw()
        except:
                self.connected=0
                val=""
        return val

    def getValCHK(self, connected):
        if connected==1:
            return self.getVal()
        else:
            self.reconnect()

    def putVal(self,val):
        try:
            self.chan.putw(val)
        except:
            self.connected=0

    def putValCHK(self, val, connected):
        if connected==1:
            self.putVal(val)
        else:
            self.reconnect()

    def reconnect(self):
        try:
            self.chan=CaChannel()
            self.chan.search(self.pvName)
            self.chan.pend_io()
            self.connected=1
        except CaChannelException, status:
            print ca.message(status)
            self.connected=0        

# --------------------------------- Functions --------------------------------------#
def show_help():
        print "USAGE"
        print "Input parameters"
        print "   [-t]  = do not run scans just test parameters (optional) "
        print "   $1  = start position (in microns)"
        print "   $2  = end position (in microns)"
        print "Optional"
        print "   $3  = binning. "
        print ""
        print "EXAMPLE"
        print "   stacked_scan.py -4200 -8000"
	print "     scan all blocks covering sample between position -4200 -8000 "
        print ""
        print "   stacked_scan.py -t -4200 -8000"
	print "     Same as above but just print parameters for total scan and"
        print "     each block;"
        print ""
        print ""
        sys.exit(0)



#-------------------Reading parameters-------------------------------
path_arg_at=0
if len(sys.argv) == 1 or len(sys.argv) > 4 or sys.argv[1]=='-h':
        show_help()
        sys.exit(1)
else:
        path_arg_at=1

testonly = 0
if path_arg_at>0:

        if len(sys.argv) - path_arg_at < 2:
                print "Startpos, endpos, number of lines and binning must be given. -t is optional" 
		show_help()
		sys.exit(1)

        # startpos
	if sys.argv[path_arg_at] == "-t" :
		testonly = 1
		path_arg_at = path_arg_at + 1
	try:
		startp = int(sys.argv[path_arg_at])
		startpos = float(startp)
	except:
		try:
			startpos = float(sys.argv[path_arg_at])
		except:
                	print "Parameter " + str(path_arg_at) + ": Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)
        # endpos
	try:
		endp = int(sys.argv[path_arg_at + 1])
		endpos = float(endp)
	except:
		try:
			endpos = float(sys.argv[path_arg_at + 1])
		except:
                	print "Parameter " + str(path_arg_at) + ": Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)
        
        # number of lines
        chSer=EpicsChannel("X02DA-ES1-CAM1:SERV_SEL")
        usedServer=chSer.getValCHK(chSer.connected)

	if usedServer==0:
		chNLines=EpicsChannel("X02DA-CCDCAM:HEIGHT")
	elif usedServer==1:
		chNLines=EpicsChannel("X02DA-CCDCAM2:HEIGHT")
	else:
		print "The server " + int(usedServer) + " is not implemented yet!"

        numlines=int(chNLines.getValCHK(chNLines.connected))
	print "Number of lines " + str(numlines)
        
        # magnification
	# Consider 2% overlapping
	
	corr_fact = 1.02
        chMag=EpicsChannel("X02DA-ES1-MS:MAGNF")
        magnify = chMag.getValCHK(chMag.connected)
	magnify = magnify*corr_fact

	print "Corrected magnification " + str(magnify) 
	
        # binning

	if testonly==0:
		try:
 			if len(sys.argv)==4:
				bin = int(sys.argv[path_arg_at + 2])
				binning = float(bin)
			elif len(sys.argv)==3:
				bin = 1
				binning = float(bin)
		except:
			print "Vertical binning factor must be an integer value." 
			show_help()
			sys.exit(1)
	elif testonly==1:
		try:
 			if len(sys.argv)==5:
				bin = int(sys.argv[path_arg_at + 3])
				binning = float(bin)
			elif len(sys.argv)==4:
				bin = 1
				binning = float(bin)
		except:
			print "Vertical binning factor must be an integer value." 
			show_help()
			sys.exit(1)

else:
	print "Error: path_arg_at: " + path_arg_at
	show_help()
	sys.exit(1)

chPitch=EpicsChannel("X02DA-ES1-CAM1:PIXL_SIZE.VAL")
pitchsize = chPitch.getValCHK(chPitch.connected)
print "Pitch size " + str(pitchsize) + " um"

pixelsize = pitchsize / magnify * binning
blocksize = float(numlines) * pixelsize
if  endpos < startpos :
	# swap end and startpos! stacked scans always start with top block first.
	# Top block is visible in field of view when sample stage is lowest in Y
	# Bottom block ist visible in field of view when stample state is highest in Y
	# -> startpos must be less than endpos -> swap if this condition is not met
	swap     = endpos
	endpos   = startpos
	startpos = swap

delta = endpos - startpos
# compute number of blocks needed to cover the distance between start and stop position;
# this is one larger than the number of full blocks fitting into delta.
# Federica, Jan 25 2008 - I think this number is twice the number of full blocks fitting into delta
# if delta cannot be divided exactly by the blocks
#print (delta/blocksize)-float(math.floor(delta/blocksize))
if (delta/blocksize)-float(math.floor(delta/blocksize))!=0.:
    nblocks = int(math.floor(delta/blocksize)) + 2
else:
    nblocks = int(math.floor(delta/blocksize)) + 1
#print math.floor(delta/blocksize)
#print delta / blocksize
#print "delta " + str(delta)
#print "blocksize " + str(blocksize)
#print "nblocks " + str(nblocks)
oversizing = float(nblocks) * blocksize - delta;
unusedlines = int(oversizing / pixelsize) 
#--------------------------------------------------------------
# Define relevant epics channels

chTrg=EpicsChannel("X02DA-SCAN-SCN1:GO")
chEndstation=EpicsChannel("X02DA-ES1-CAM1:ENDST_SEL")


usedEndstation=chEndstation.getValCHK(chEndstation.connected)
if usedEndstation==0:
	chYLIN=EpicsChannel("X02DA-ES1-SMP1:TRY-VAL")
	chYLINM1=EpicsChannel("X02DA-ES1-SMP1:TRY1.DMOV")
  	chYLINM2=EpicsChannel("X02DA-ES1-SMP1:TRY2.DMOV")
elif usedEndstation==1:
   	chYLIN=EpicsChannel("X02DA-ES1-SMP2:TRY-VAL")
   	chYLINM1=EpicsChannel("X02DA-ES1-SMP2:TRY1.DMOV")
   	chYLINM2=EpicsChannel("X02DA-ES1-SMP2:TRY2.DMOV")
else:
	print "The endstation " + str(usedEndstation) + " is not implemented yet!"
	
chFNAME=EpicsChannel("X02DA-SCAN-CAM1:FILPRE")
chFDIR=EpicsChannel("X02DA-SCAN-CAM1:FILDIR")
chROI=EpicsChannel("X02DA-SCAN-CAM1:ROI")

chRingCurrent=EpicsChannel("ARIDI-PCT:CURRENT")
chInterlock=EpicsChannel("X02DA-FE-AB1:ILK-STATE")
chAbsorberStatus=EpicsChannel("X02DA-FE-AB1:CLOSE4BL")

fileprefix=chFNAME.getValCHK(chFNAME.connected)
CurrentStart=chRingCurrent.getValCHK(chRingCurrent.connected)

print "####################################################################"
print "Sample base name .................: " + fileprefix
print "Start position for YLIN ..........: " + str(startpos) + " microns"
print "End position for YLIN ............: " + str(endpos) + " microns"
print "Number of Y-blocks to scan........: " + str(nblocks)
print "size of the Y-block ..............: " + str(blocksize) + " microns"
print "Total number of lines to scan ....: " + str(numlines * nblocks )
print "Total number of lines requested ..: " + str(numlines * nblocks - unusedlines )
print 


newfileprefix = ""

print "Multiple YLIN scan started!"
i=0
lastscan=0
while i<nblocks:
#for i in range(0,nblocks):

	# Check beamline status
	beam_dump=0
	previous=0

        if testonly != 1:
        	CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
        	AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
        	Interlock=chInterlock.getValCHK(chInterlock.connected)

        	while (CurrentStatus <= (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
			beam_dump=1
			previous=1
        		time.sleep(0.5)
        		CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
        		AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
        		Interlock=chInterlock.getValCHK(chInterlock.connected)
		
			if (CurrentStatus >= (CurrentStart-0.05*CurrentStart) and Interlock==0 and AbsorberStatus==0):
				print "\nThe absorber has been closed by the interlock!!!"
        			chAbsorberStatus.putValCHK(1,chAbsorberStatus.connected)
         			print "Waiting 60s for thermal compensation after the absorber has been closed ...\n"
        			time.sleep(60)

		if beam_dump==1:
			beam_dump=0
			if i!=0:
				if lastscan==0:
					i=i-1
				else:
					lastscan=0
				print "Previous scan is done again!"
			else:
				previous=0
		
        print "************************************************************"
        
        print "Settings for block number..: " + str(i+1)
        
        #Calculate initial position and corresponding filename
        position=startpos+i*blocksize
	if previous==0:
	        newROI="B"+str( i + 1 )
        	newfileprefix=fileprefix+"_B"+str( i + 1 ) + "_"
	else:
		previous=0
	        newROI=newROI + "b"
		newfileprefix=fileprefix + "_" + newROI + "_"
		#newfileprefix=newfileprefix + "b"

        #Set filename
	if testonly == 1 :
		print "New file prefix...................: " + newfileprefix
        	print "Block position....................: " + str(position)
		i=i+1
		#if i + 1 == nblocks :
		#	print "Scan endposition at line ..........: " + str(numlines - unusedlines)
		#else :
		#	print "Scan endposition at line ..........: "
		continue
	chROI.putValCHK(newROI,chROI.connected)
	print "New file prefix...................: " + newfileprefix
        #Wait 5 seconds for postfix to be set...!!!
        time.sleep(5)

        #Move to right position
        print "Move YLIN to position.............: " + str(position)
        chYLIN.putValCHK(position,chYLIN.connected)
        print "Wait for Y motors ... "
	moved1 = chYLINM1.getValCHK(chYLINM1.connected)
	moved2 = chYLINM2.getValCHK(chYLINM2.connected)
	while not moved1 or not moved2 :
		time.sleep(1)
		moved1 = chYLINM1.getValCHK(chYLINM1.connected)
		moved2 = chYLINM2.getValCHK(chYLINM2.connected)

        # Wait 10 seconds for motor moving...Hardcoded!!!
        # time.sleep(10)
        
        # Check beamline status
        CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
        AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
        Interlock=chInterlock.getValCHK(chInterlock.connected)

        while (CurrentStatus <= (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
        	time.sleep(0.5)
        	CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
        	AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
        	Interlock=chInterlock.getValCHK(chInterlock.connected)
		
		if (CurrentStatus >= (CurrentStart-0.05*CurrentStart) and Interlock==0 and AbsorberStatus==0):
			print "\nThe absorber has been closed by the interlock!!!"
        		chAbsorberStatus.putValCHK(1,chAbsorberStatus.connected)
         		print "Waiting 60s for thermal compensation after the absorber has been closed ...\n"
        		time.sleep(60)
	
        # Start tomoscan
        print "Acquiring tomo data for block " + str(i+1) + "....."
        chTrg.putValCHK(1,chTrg.connected)
        
        waitflag = 1
        
        while waitflag == 1:
                time.sleep(1)
                scanstatus=chTrg.getValCHK(chTrg.connected)
                
                if scanstatus == 0:
                        waitflag = 0
                else:
                        waitflag = 1
                        
        logpath = chFDIR.getValCHK(chFDIR.connected)
	logfile = logpath + "/tif/" + newfileprefix + ".log"
        print "************************************************************"
	openlogfile = 0
	try :
		logfile = open(logfile,"a")
		openlogfile = 1
        	loglinetext =             "\n------------------------------------------------------------\n"
		loglinetext = loglinetext + "Scan start postion : " + str( startpos ) + "\n"
		loglinetext = loglinetext + "Scan end postion : " + str( endpos ) + "\n"
		loglinetext = loglinetext + "Block position : " + str(position) + "\n"
		loglinetext = loglinetext + "Block number : " + str( i + 1 ) + "/" + str(nblocks) + "\n"
		loglinetext = loglinetext + "Block size : " + str(blocksize) + "\n"
		loglinetext = loglinetext + "Number of lines in block : " + str(numlines) + "\n"
		loglinetext = loglinetext + "Total number of scanned lines : " + str(numlines * ( i + 1 ) ) + "\n"
		loglinetext = loglinetext + "Total number of lines requested : " + str(numlines * ( i + 1 ) - unusedlines ) + "\n"
		loglinetext = loglinetext + "Scan end position at line : " 
		if i + 1 == nblocks :
			loglinetext = loglinetext + str(numlines - unusedlines)
		loglinetext = loglinetext + "\n"
        	loglinetext = loglinetext + "------------------------------------------------------------\n"
		logfile.write(loglinetext)
		logfile.close()
	except :
		if openlogfile == 1 :
			logfile.close()
			
        # Check beamline status

        if (i==nblocks-1):
        	CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
        	AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
        	Interlock=chInterlock.getValCHK(chInterlock.connected)
        	if (CurrentStatus <= (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
 			print "Last scan needs to be repeated!"
			i=i-1
			lastscan=1			

        i=i+1
	
#Set ROI channel back to empty
ROI=""
chROI.putValCHK(ROI,chROI.connected)

print "Multiple YLIN scan done!!! Thank you for flying TOMCAT!"

