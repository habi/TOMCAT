from glob import glob
from PIL import Image
import os,sys
import numpy
sOffset=0
angOffset=180.01

if len(sys.argv)<2: sliceNumber=1000
else: sliceNumber=int(sys.argv[1])


def processImage(inFile,outFile,scanNumber):
	cImg=Image.open(inFile)
	cImg=cImg.rotate(scanNumber*angOffset+sOffset)# ,filter=Image.BILINEAR,expand=0)
	#pix=numpy.array(cImg.getdata()).reshape(cImg.size[0],cImg.size[1])
	
	#if(scanNumber%2==1): print ('flipping',scanNumber) #pix=numpy.flipud(pix) #numpy.rot90(pix,2)
	#cImg.putdata(list(tuple(pixel) for pixel in pix))
	cImg.save(outFile)
	#return pix
def generate_slices(sliceNumber):
	outDirName="slicedir_%04d" % (sliceNumber)
	imglist=glob("rec*/*%04d*.tif" % (sliceNumber))
	if len(imglist)<1: 
		print "No Images found"
		return
	scanNumber=map(lambda x: int(x.split('/')[-2].split('_')[-1]),imglist)
	imgdict=dict(zip(scanNumber,imglist))
	
	if (not os.path.exists(outDirName)): os.makedirs(outDirName)
	map(lambda i: processImage(imgdict[i],outDirName+"/%03d.tif" % (i),i),sorted(imgdict.keys()))

if sliceNumber>=0:
	generate_slices(sliceNumber)
else:
	for islice in range(1,2560,-1*sliceNumber): generate_slices(islice)
