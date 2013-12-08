# Multiscan Viewer
# Kevin Mader (kevin.mader@gmail.com)
#
# Takes a given slice out of a folder of reconstructions and makes a folder filled with those images
# Input parameter is slice to take, a negative number takes slices every input slices between 0 and 3000 to make multiple
# In the sample directory run
#    python ~/beamline-scripts/postscan/multiscanViewer.py 1601
# To run for all samples
# for cdir in *; do cd $cdir; python ~/beamline-scripts/postscan/multiscanViewer.py 1200; cd ..; done
from glob import glob
from PIL import Image
import os,sys
import numpy
# starting offset
sOffset=0
# offset between scans (!! caution in Scientific Linux mindblowingly shitty python/PIL 
# implementation a rotation of exactly 180 rotate(180) on 16 bit integer images you get garbage 
angOffset=180-0.001 # (1.0/15000001.0*180.0)

if len(sys.argv)<2: sliceNumber=1000
else: sliceNumber=int(sys.argv[1])
sampleName=os.path.abspath('.').split('/')[-1]

def processImage(inFile,outFile,scanNumber):
	cImg=Image.open(inFile)
	cImg=cImg.rotate(scanNumber*angOffset+sOffset)
	cImg.save(outFile)

def generate_slices(sliceNumber):
	outDirName="slicedir_%04d" % (sliceNumber)
	# read images
	imglist=glob("rec*/*%04d*.tif" % (sliceNumber))
	if len(imglist)<1: 
		print "No Images found"
		return
	# extract the scan number from the path (custom to multiple scans made with kevins script)
	scanNumber=map(lambda x: int(x.split('/')[-2].split('_')[-1]),imglist)
	# create a mapping (dictionary) between the scan number and the path name
	imgdict=dict(zip(scanNumber,imglist))
	# if the output directory doesnt exist create it
	if (not os.path.exists(outDirName)): os.makedirs(outDirName)
	# format for the output name
	outNameFn=lambda i: outDirName+"/%s.%04d.%03d.tif" % (sampleName,sliceNumber,i)
	# run for every scan
	map(lambda i: processImage(imgdict[i],outNameFn(i),i),sorted(imgdict.keys()))
	print ('Slice %04d with offset %02.2f generated for scans:' % (sliceNumber,angOffset),imgdict.keys())

if sliceNumber>=0:
	# run for just one slice
	generate_slices(sliceNumber)
else:
	# run for every -sliceNumber slices between between 1 and 2560
	map(generate_slices,range(1,2560,-1*sliceNumber))
