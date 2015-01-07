#!/usr/bin/python
# -*- coding: utf8 -*-

"""
Multiscan Viewer
 Kevin Mader (kevin.mader@gmail.com)

 Takes a given slice out of a folder of reconstructions and makes a folder filled with those images. Designed originally for multiple scans done
 with the ManyScanReconHDF5.cmd but has been generalized to work with any prefix
 Input parameter is slice to take, a negative number takes slices every input slices between 0 and 3000 to make multiple
 In the sample directory run
    python ~/beamline-scripts/postscan/multiscanViewer.py -l 1601
 To run for all samples
 for cdir in *; do cd $cdir; python ~/beamline-scripts/postscan/multiscanViewer.py 1200; cd ..; done
"""

from optparse import OptionParser
from glob import glob
from PIL import Image
import os,sys
import numpy

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-s', '--scanprefix', dest='scan_prefix', help='Scan Prefix Name use % instead of star since linux interprets all stars',default='rec',metavar='rec')
parser.add_option('-a', '--angle', dest='angle', help='Angle offset between sizes', metavar='180',default=180-0.001)
parser.add_option('-i', '--initialangle', dest='initial_angle', help='Initial Angle', metavar='0',default=0)
parser.add_option('-l', '--slice', dest='slice', help='Slice number to take from each scan', metavar='1000',default=1000)
parser.add_option('-m', '--multiplefolders',dest='multiple',help='Measurements are in seperate folders',action='store_true',default=False)
(options, args) = parser.parse_args()


# starting offset
sOffset = float(options.initial_angle)
# offset between scans (!! caution in Scientific Linux mindblowingly shitty python/PIL
# implementation a rotation of exactly 180 rotate(180) on 16 bit integer images you get garbage
angOffset = float(options.angle)
multiple = options.multiple
sliceNumber = int(options.slice)
sampleName=os.path.abspath('.').split('/')[-1]
scan_prefix='*'.join(options.scan_prefix.split('%')) # replace & with *


def processImage(inFile,outFile,scanNumber):
	cImg=Image.open(inFile)
	cImg=cImg.rotate(scanNumber*angOffset+sOffset)
	cImg.save(outFile)

def generate_slices(folder_prefix,sliceNumber):
	outDirName="slicedir_%03d" % (sliceNumber)
	# read images
	list_cmd=folder_prefix+"*/*%03d.rec*.tif" % (sliceNumber)

	imglist=glob(list_cmd)
	print (list_cmd,imglist)
	if len(imglist)<1:
		print "No Images found"
		return
	nameIndex=-2
	# extract the scan number from the path (custom to multiple scans made with kevins script)

	try:
	    if multiple:
	    	scanNumber=range(len(imglist))
		scanNames=map(lambda x: x.split('/')[-3],imglist) # just the folder name
	    else:
	    	scanNumber=map(lambda x: int(x.split('/')[-2].split('_')[-1]),imglist) # a scan number extracted from the folder
		scanNames=map(lambda i: '%03d' % i,scanNumber)
	except:
	    print 'Scan Number could not be automatically extracted'
	    imglist=sorted(imglist)
	    scanNumber=range(len(imglist))
	    scanNames=map(lambda i: '%03d' % i,scanNumber)
	# create a mapping (dictionary) between the scan number and the path name
	imgdict=dict(zip(scanNumber,imglist))
	scanNameDict = dict(zip(scanNumber,scanNames))
	# if the output directory doesnt exist create it
	if (not os.path.exists(outDirName)): os.makedirs(outDirName)
	# format for the output name
	outNameFn=lambda i: outDirName+"/%s.%04d.%s.tif" % (sampleName,sliceNumber,str(i))
	# run for every scan
	map(lambda i: processImage(imgdict[i],outNameFn(scanNameDict[i]),i),sorted(imgdict.keys()))
	print ('Slice %04d with offset %02.2f generated for scans:' % (sliceNumber,angOffset),imgdict.keys())

if sliceNumber>=0:
	# run for just one slice
	generate_slices(scan_prefix,sliceNumber)
else:
	# run for every -sliceNumber slices between between 1 and 2560
	map(lambda cslice: generate_slices(scan_prefix,cslice),range(1,2160,-1*sliceNumber))
