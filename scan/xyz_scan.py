#! /usr/bin/env python

import sys
import os.path
import string
import commands
import math
import numpy as np
import random
import time


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

# here I add the new entries

def show_help():
        print "USAGE"
        print "Input parameters"
        print "   [-t]  = do not run scans just test parameters (optional) "
        print "   $1  = xx start position (in microns)"
        print "   $2  = xx end position (in microns)"
        print "   $3  = zz start position (in microns)"
        print "   $4  = zz end position (in microns)"
        print "   $5  = y start position (in microns)"
        print "   $6  = y end position (in microns)"
        print "   $7  = number of horizontal lines in projections"
        print "   $8  = number of vertical lines in projections"
        print "   $9  = binning. "
        print ""
        print "EXAMPLE"
        print "   xyz_stacked_scan.py -100 275 -200 223 -4200 -8000 2560 2160"
	print "     scan all blocks covering sample between position -100 275 in xx"	
	print "     scan all blocks covering sample between position -200 223 in zz"
	print "     scan all blocks covering sample between position -4200 -8000 in y"
	print "     using a field of view of 2560 x 2160 FOV"
        print ""
        print "   xyz_stacked_scan.py -t -100 275 -200 223 -4200 -8000 2560 2160"
	print "     Same as above but just print parameters for total scan and"
        print "     each block;"
        print ""
        print ""
        sys.exit(0)



#-------------------Reading parameters-------------------------------
path_arg_at=0
print str(sys.argv)
if len(sys.argv) == 1 or len(sys.argv) > 10 or sys.argv[1]=='-h':
        show_help()
        sys.exit(1)
else:
        path_arg_at=1

testonly = 0
if path_arg_at>0:

        if len(sys.argv) - path_arg_at < 8:
                print "xx startpos, xx endpos, zz startpos, zz endpos, y startpos, y endpos, number of horizontal and vertical lines must be given. -t is optional" 
		show_help()
		sys.exit(1)

	if sys.argv[path_arg_at] == "-t" :
		testonly = 1
		path_arg_at = path_arg_at + 1
	
        # xx startpos
	try:
		xxstartp = int(sys.argv[path_arg_at])
		xxstartpos = float(xxstartp)
	except:
		try:
			xxstartpos = float(sys.argv[path_arg_at])
		except:
                	print "Parameter " + str(path_arg_at) + ": xx Start Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)
        # xx endpos
	try:
		xxendp = int(sys.argv[path_arg_at + 1])
		xxendpos = float(xxendp)
	except:
		try:
			xxendpos = float(sys.argv[path_arg_at + 1])
		except:
                	print "Parameter " + str(path_arg_at) + ": xx End Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)
        

        # zz startpos
	try:
		zzstartp = int(sys.argv[path_arg_at + 2])
		zzstartpos = float(zzstartp)
	except:
		try:
			zzstartpos = float(sys.argv[path_arg_at + 2])
		except:
                	print "Parameter " + str(path_arg_at) + ": zz Start Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)
        # zz endpos
	try:
		zzendp = int(sys.argv[path_arg_at + 3])
		zzendpos = float(zzendp)
	except:
		try:
			zzendpos = float(sys.argv[path_arg_at + 3])
		except:
                	print "Parameter " + str(path_arg_at) + ": zz End Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)

        # y startpos
	try:
		ystartp = int(sys.argv[path_arg_at + 4])
		ystartpos = float(ystartp)
	except:
		try:
			ystartpos = float(sys.argv[path_arg_at + 4])
		except:
                	print "Parameter " + str(path_arg_at) + ": zz Start Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)
        # y endpos
	try:
		yendp = int(sys.argv[path_arg_at + 5])
		yendpos = float(yendp)
	except:
		try:
			yendpos = float(sys.argv[path_arg_at + 5])
		except:
                	print "Parameter " + str(path_arg_at) + ": zz End Position is not a number; misstyped test flag?? "
			show_help()
			sys.exit(1)


        # number of horizontal lines
	try:
 		hnumlines = int(sys.argv[path_arg_at + 6])
	except:
                print "Number of horizontal lines must be an integer value." 
		show_help()
		sys.exit(1)
        
        # number of vertical lines
	try:
 		vnumlines = int(sys.argv[path_arg_at + 7])
	except:
                print "Number of vertical lines must be an integer value." 
		show_help()
		sys.exit(1)

        # magnification
	# Consider 2% overlapping
	
	corr_fact = 1.02
        chMag=EpicsChannel("X02DA-ES1-MS:MAGNF")
        magnify = chMag.getValCHK(chMag.connected)
	magnify = magnify*corr_fact

	print "Corrected magnification " + str(magnify)

	if path_arg_at == 1 and len(sys.argv) > 9 :
                print "Invalid number of parameters: optional flags must be specified before scan parameters" 
		show_help()
		sys.exit(1)

else:
	print "Error: path_arg_at: " + path_arg_at
	show_help()
	sys.exit(1)

binning=1
chPitch=EpicsChannel("X02DA-ES1-CAM1:PIXL_SIZE.VAL")
pitchsize = chPitch.getValCHK(chPitch.connected)
print "Pitch size " + str(pitchsize) + " um"
pixelsize = pitchsize / magnify * binning


# blocks definition in y
yblocksize = round(float(vnumlines) * pixelsize,1)

if  yendpos < ystartpos :
	# swap end and startpos! stacked scans always start with top block first.
	# Top block is visible in field of view when sample stage is lowest in Y
	# Bottom block ist visible in field of view when stample state is highest in Y
	# -> startpos must be less than endpos -> swap if this condition is not met
	swap     = yendpos
	yendpos   = ystartpos
	ystartpos = swap

ydelta = yendpos - ystartpos
# compute number of blocks needed to cover the distance between start and stop position;
# this is one larger than the number of full blocks fitting into delta.
# Federica, Jan 25 2008 - I think this number is twice the number of full blocks fitting into delta
# if delta cannot be divided exactly by the blocks
#print (delta/blocksize)-float(math.floor(delta/blocksize))
if (ydelta/yblocksize)-float(math.floor(ydelta/yblocksize))!=0.:
    nyblocks = int(math.floor(ydelta/yblocksize)) + 2
else:
    nyblocks = int(math.floor(ydelta/yblocksize)) + 1
#print math.floor(delta/blocksize)
#print delta / blocksize
#print "delta " + str(delta)
#print "blocksize " + str(blocksize)
#print "nblocks " + str(nblocks)
#yoversizing = float(nyblocks) * yblocksize - ydelta;
#yunusedlines = int(yoversizing / pixelsize) 
#--------------------------------------------------------------

# blocks definition in xx

# block defined to take in account the squared inside the CT circle
xxblocksize = round(float(hnumlines) * pixelsize * np.sqrt(2) / 2.,1) 

if  xxendpos < xxstartpos :
	# swap end and startpos! stacked scans always start with positive block first.
	# -> startpos must be less than endpos -> swap if this condition is not met
	swap     = xxendpos
	xxendpos   = xxstartpos
	xxstartpos = swap

xxdelta = xxendpos - xxstartpos
# compute number of blocks needed to cover the distance between start and stop position;
# this is one larger than the number of full blocks fitting into delta.
# Federica, Jan 25 2008 - I think this number is twice the number of full blocks fitting into delta
# if delta cannot be divided exactly by the blocks
#print (delta/blocksize)-float(math.floor(delta/blocksize))
if (xxdelta/xxblocksize)-float(math.floor(xxdelta/xxblocksize))!=0.:
    nxxblocks = int(math.floor(xxdelta/xxblocksize)) + 2
else:
    nxxblocks = int(math.floor(xxdelta/xxblocksize)) + 1
#print math.floor(delta/blocksize)
#print delta / blocksize
#print "delta " + str(delta)
#print "blocksize " + str(blocksize)
#print "nblocks " + str(nblocks)
xxoversizing = float(nxxblocks) * xxblocksize - xxdelta;
xxunusedlines = int(xxoversizing / pixelsize) * np.sqrt(2) / 2.

# blocks definition in zz

# block defined to take in account the squared inside the CT circle
zzblocksize = round(float(hnumlines) * pixelsize * np.sqrt(2) / 2.,1) 

if  zzendpos < zzstartpos :
	# swap end and startpos! stacked scans always start with positive block first.
	# -> startpos must be less than endpos -> swap if this condition is not met
	swap     = zzendpos
	zzendpos   = zzstartpos
	zzstartpos = swap

zzdelta = zzendpos - zzstartpos
# compute number of blocks needed to cover the distance between start and stop position;
# this is one larger than the number of full blocks fitting into delta.
# Federica, Jan 25 2008 - I think this number is twice the number of full blocks fitting into delta
# if delta cannot be divided exactly by the blocks
#print (delta/blocksize)-float(math.floor(delta/blocksize))
if (zzdelta/zzblocksize)-float(math.floor(zzdelta/zzblocksize))!=0.:
    nzzblocks = int(math.floor(zzdelta/zzblocksize)) + 2
else:
    nzzblocks = int(math.floor(zzdelta/xxblocksize)) + 1
#print math.floor(delta/blocksize)
#print delta / blocksize
#print "delta " + str(delta)
#print "blocksize " + str(blocksize)
#print "nblocks " + str(nblocks)
zzoversizing = float(nzzblocks) * zzblocksize - zzdelta;
zzunusedlines = int(zzoversizing / pixelsize) * np.sqrt(2) / 2.
#--------------------------------------------------------------

# Define relevant epics channels

chTrg=EpicsChannel("X02DA-SCAN-SCN1:GO")

chYLIN=EpicsChannel("X02DA-ES1-SMP1:TRY-VAL")
chYLINM1=EpicsChannel("X02DA-ES1-SMP1:TRY1.DMOV")
chYLINM2=EpicsChannel("X02DA-ES1-SMP1:TRY2.DMOV")
chFNAME=EpicsChannel("X02DA-SCAN-CAM1:FILPRE")
chFDIR=EpicsChannel("X02DA-SCAN-CAM1:FILDIR")
chROI=EpicsChannel("X02DA-SCAN-CAM1:ROI")

chXXLIN=EpicsChannel("X02DA-ES1-SMP1:TRXX.VAL")
chZZLIN=EpicsChannel("X02DA-ES1-SMP1:TRZZ.VAL")


chRingCurrent=EpicsChannel("ARIDI-PCT:CURRENT")
chInterlock=EpicsChannel("X02DA-FE-AB1:ILK-STATE")
chAbsorberStatus=EpicsChannel("X02DA-FE-AB1:CLOSE4BL")

fileprefix=chFNAME.getValCHK(chFNAME.connected)
CurrentStart=chRingCurrent.getValCHK(chRingCurrent.connected)

print "####################################################################"
print "Sample base name ............................: " + fileprefix
print "Start position for YLIN .....................: " + str(ystartpos) + " microns"
print "End position for YLIN .......................: " + str(yendpos) + " microns"
print "Start position for XXLIN ....................: " + str(xxstartpos) + " microns"
print "End position for XXLIN ......................: " + str(xxendpos) + " microns"
print "Start position for ZZLIN ....................: " + str(zzstartpos) + " microns"
print "End position for ZZLIN ......................: " + str(zzendpos) + " microns"

print "Total number of blocks to scan...............: " + str(nxxblocks * nzzblocks * nyblocks)

print "Number of XX-blocks .........................: " + str(nxxblocks)
print "size of the XX-block ........................: " + str(xxblocksize) + " microns"
print "Number of ZZ-blocks .........................: " + str(nzzblocks)
print "size of the ZZ-block ........................: " + str(zzblocksize) + " microns"
print "Number of Y-blocks ..........................: " + str(nyblocks)
print "size of the Y-block .........................: " + str(yblocksize) + " microns"

#print "Total number of vertical lines to scan ....: " + str(ynumlines * nyblocks )
#print "Total number of vertical lines requested ..: " + str(ynumlines * nyblocks - yunusedlines )

print

newfileprefix = ""
print "Multiple XYZ scan started!"
i=0

lastscan=0
while i<nyblocks:
#for i in range(0,nblocks):

	yposition=ystartpos+i*yblocksize
	
	#Move to right positions in Y
	
	if testonly == 0 :
		print "Move YLIN to position.............: " + str(yposition)
		chYLIN.putValCHK(yposition,chYLIN.connected)
		print "Wait for Y motors ... "
		moved1 = chYLINM1.getValCHK(chYLINM1.connected)
		moved2 = chYLINM2.getValCHK(chYLINM2.connected)
		while not moved1 or not moved2 :
			time.sleep(1)
			moved1 = chYLINM1.getValCHK(chYLINM1.connected)
			moved2 = chYLINM2.getValCHK(chYLINM2.connected)
	j=0
	
	while j<nzzblocks:

		zzposition=zzstartpos+j*zzblocksize
		
		#Move to right positions in ZZ
		if testonly == 0 :
			print "Move ZZ to position.............: " + str(zzposition)
			chZZLIN.putValCHK(zzposition,chZZLIN.connected)
			print "Wait for ZZ motors ... "
			moved1 = chZZLIN.getValCHK(chZZLIN.connected)
			while not moved1 :
				time.sleep(1)
				moved1 = chZZLIN.getValCHK(chZZLIN.connected)
				
			
		k=0
		
		while k<nxxblocks:

		# Check beamline status
			beam_dump=0
			previous=0

			if testonly != 1:
				CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
				AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
				Interlock=chInterlock.getValCHK(chInterlock.connected)
			
			#CHANGE HERE the while
				while (CurrentStatus <= (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
				#while (CurrentStatus == (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
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
						# TO CHANGE
						time.sleep(60)

				if beam_dump==1:
					beam_dump=0
					if lastscan==0:
						if k!=0:
							k=k-1
						else:
						      if j!=0:
							      j=j-1
							      k=nxxblocks-1
						      else:
							      if i!=0:
								      i=i-1
								      j=nzzblocks-1
								      k=nxxblocks-1
						      lastscan=0
					print "Previous scan is done again!"
					print "Checking the positions"
					yposition=ystartpos+i*yblocksize
					yactual=chYLIN.getValCHK(chYLIN.connected)
					yactual=yposition
					if (abs(yposition-yactual)>=5):#more than 5 microns

					    print "Move YLIN to position.............: " + str(yposition)
					    chYLIN.putValCHK(yposition,chYLIN.connected)
					    print "Wait for Y motors ... "
					    moved1 = chYLINM1.getValCHK(chYLINM1.connected)
					    moved2 = chYLINM2.getValCHK(chYLINM2.connected)
					    while not moved1 or not moved2 :
					    	time.sleep(1)
					    	moved1 = chYLINM1.getValCHK(chYLINM1.connected)
					    	moved2 = chYLINM2.getValCHK(chYLINM2.connected)

					zzposition=zzstartpos+j*zzblocksize
					zzactual=chZZLIN.getValCHK(chZZLIN.connected)
					zzactual=zzposition
					if (abs(zzposition-zzactual)>=5):#more than 5 microns
					     print "Move ZZ to position.............: " + str(zzposition)
					     chZZLIN.putValCHK(zzposition,chZZLIN.connected)
					     print "Wait for ZZ motors ... "
					     moved1 = chZZLIN.getValCHK(chZZLIN.connected)
					     while not moved1 :
					     	time.sleep(1)
					     	moved1 = chZZLIN.getValCHK(chZZLIN.connected)
					# xx is done later
					else:
						previous=0
		
			print "************************************************************"
        
			print "Settings for XX block number..: " + str(k+1)
			print "Settings for ZZ block number..: " + str(j+1)
			print "Settings for Y  block number..: " + str(i+1)


			#Calculate initial positions and corresponding filename

			xxposition=xxstartpos+k*xxblocksize

			if previous==0:
				#newROI="X"+str( k + 1 )+"_Y"+str( i + 1 )+"_Z"+str( j +1)
				newROI="B"+str( i * ( nxxblocks * nzzblocks ) + j * ( nxxblocks ) + k +1)

				#newfileprefix=fileprefix+"X"+str( k + 1 )+"_Y"+str( i + 1 )+"_Z"+str( j +1) + "_"
				newfileprefix=fileprefix+"_B"+str( i * ( nxxblocks * nzzblocks ) + j * ( nxxblocks ) + k +1)+"_"
			else:
				previous=0
				newROI=newROI + "b"
				newfileprefix=fileprefix + "_" + newROI + "_"
				#newfileprefix=newfileprefix + "b"

			#Set filename
			if testonly == 1 :
				print "New file prefix...................: " + newfileprefix
				print "Block xx position....................: " + str(xxposition)
				print "Block zz position....................: " + str(zzposition)
				print "Block y position....................: " + str(yposition)
				#i=i+1
				#j=j+1
				k=k+1
				
		#if i + 1 == nblocks :

		#	print "Scan endposition at line ..........: " + str(numlines - unusedlines)
		#else :
		#	print "Scan endposition at line ..........: "
				continue
			chROI.putValCHK(newROI,chROI.connected)
			print "New file prefix...................: " + newfileprefix
			#Wait 5 seconds for postfix to be set...!!!
			time.sleep(5)

# to be set to the right loop/while

			#Move to right positions in XX
			print "Move XX to position.............: " + str(xxposition)
			chXXLIN.putValCHK(xxposition,chXXLIN.connected)
			print "Wait for XX motors ... "
			moved1 = chXXLIN.getValCHK(chXXLIN.connected)
			while not moved1 :
				time.sleep(1)
				moved1 = chXXLIN.getValCHK(chXXLIN.connected)



			# Wait 10 seconds for motor moving...Hardcoded!!!
			# time.sleep(10)
        
			# Check beamline status
			CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
			AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
			Interlock=chInterlock.getValCHK(chInterlock.connected)

			while (CurrentStatus <= (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
			#while (CurrentStatus == (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
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
			print "Acquiring tomo data for block " + str(i*nzzblocks*nxxblocks+j*nxxblocks+k+1) + " over " + str(nyblocks*nzzblocks*nxxblocks) + "..."
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
				loglinetext = loglinetext + "Scan xx start position : " + str( xxstartpos ) + "\n"
				loglinetext = loglinetext + "Scan xx end position : " + str( xxendpos ) + "\n"
				loglinetext = loglinetext + "Scan zz start position : " + str( zzstartpos ) + "\n"
				loglinetext = loglinetext + "Scan zz end position : " + str( zzendpos ) + "\n"
				loglinetext = loglinetext + "Scan y start position : " + str( ystartpos ) + "\n"
				loglinetext = loglinetext + "Scan y end position : " + str( yendpos ) + "\n"

				loglinetext = loglinetext + "Block xx position : " + str(xxposition) + "\n"
				loglinetext = loglinetext + "Block zz position : " + str(zzposition) + "\n"
				loglinetext = loglinetext + "Block y position : " + str(yposition) + "\n"

				loglinetext = loglinetext + "Block number : " + str( i + 1 ) + "/" + str(nblocks) + "\n"

				loglinetext = loglinetext + "Block xx size : " + str(xxblocksize) + "\n"
				loglinetext = loglinetext + "Block zz size : " + str(zzblocksize) + "\n"
				loglinetext = loglinetext + "Block y size : " + str(yblocksize) + "\n"

#				loglinetext = loglinetext + "Number of lines in block : " + str(numlines) + "\n"
#				loglinetext = loglinetext + "Total number of scanned lines : " + str(numlines * ( i + 1 ) ) + "\n"
#				loglinetext = loglinetext + "Total number of lines requested : " + str(numlines * ( i + 1 ) - unusedlines ) + "\n"
#				loglinetext = loglinetext + "Scan end position at line : " 
				#if i*j*k + 1 == nxxblocks * nzzblocks * nyblocks :
					#loglinetext = loglinetext + str(numlines - unusedlines)
				loglinetext = loglinetext + "\n"
				loglinetext = loglinetext + "------------------------------------------------------------\n"
				logfile.write(loglinetext)
				logfile.close()
			except :
				if openlogfile == 1 :
					logfile.close()
			
			# Check beamline status

			if (i*j*k==nxxblocks * nzzblocks * nyblocks-1):
				CurrentStatus=chRingCurrent.getValCHK(chRingCurrent.connected)
				AbsorberStatus=chAbsorberStatus.getValCHK(chAbsorberStatus.connected)
				Interlock=chInterlock.getValCHK(chInterlock.connected)
				if (CurrentStatus <= (CurrentStart-0.05*CurrentStart) or Interlock==1 or AbsorberStatus==0):
					print "Last scan needs to be repeated!"
					i=i-1
					lastscan=1			

			k=k+1


		
		j=j+1
        
	i=i+1

#Set ROI channel back to empty
ROI=""
chROI.putValCHK(ROI,chROI.connected)

print "Multiple XYZ scan done!!! Thank you for flying TOMCAT!"