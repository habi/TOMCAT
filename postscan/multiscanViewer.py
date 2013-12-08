from glob import glob
from PIL import Image
import os,sys
import numpy
sOffset=0
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
	imglist=glob("rec*/*%04d*.tif" % (sliceNumber))
	if len(imglist)<1: 
		print "No Images found"
		return
	scanNumber=map(lambda x: int(x.split('/')[-2].split('_')[-1]),imglist)
	imgdict=dict(zip(scanNumber,imglist))
	
	if (not os.path.exists(outDirName)): os.makedirs(outDirName)
	outNameFn=lambda i: outDirName+"/%s.%04d.%03d.tif" % (sampleName,sliceNumber,i)
	map(lambda i: processImage(imgdict[i],outNameFn(i),i),sorted(imgdict.keys()))
	print ('Slice %04d with offset %02.2f generated for scans:' % (sliceNumber,angOffset),imgdict.keys())

if sliceNumber>=0:
	generate_slices(sliceNumber)
else:
	for islice in range(1,2560,-1*sliceNumber): generate_slices(islice)
