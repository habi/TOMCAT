"""
Script to find the best "overlap" from merged scans.
Even when setting the overlap to a certain value (-c 1.1 in stacked-scan.py),
the overlap might not be exactly the given one.
If one wants to merge all the subscans to a merged dataset this script can help
with finding the best match between the reconstructed slices.
It does this by loading the lowest image from stack N and calculating the
absolute difference to the top images from stack N+1.
"""

from __future__ import division
import glob
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time
import gc


def readDMP(fileName):
    '''
    Opens and reads DMP file.
    Returns numpy ndarray.
    From Martin Nyvlts DMP reader, available on
    intranet.psi.ch/wiki/bin/viewauth/Tomcat/BeamlineManual#The_DMP_file_format
    '''

    fd = open(fileName, 'rb')

    #datatype is unsigned short
    datatype = 'h'
    numberOfHeaderValues = 3

    headerData = np.fromfile(fd, datatype, numberOfHeaderValues)

    imageShape = (headerData[1], headerData[0])

    imageData = np.fromfile(fd, np.float32, -1)
    imageData = imageData.reshape(imageShape)

    fd.close()

    return imageData

StartPath = '/sls/X02DA/data/e15171/Data10/disk1'
FolderList = glob.glob(os.path.join(StartPath, 'Cand2_265_a_*'))

SampleName = [os.path.basename(i) for i in FolderList]
RecFolder = [glob.glob(os.path.join(i, '*DMP*'))[0] for i in FolderList]

for c, i in enumerate(SampleName):
    print 'Sample', i, 'contains the rec folder', RecFolder[c]
print 80 * '-'

path1 = '/sls/X02DA/data/e15171/Data10/disk1/Cand2_265_a_B3_/rec_DMP_Paganin_0/Cand2_265_a_B3_399.rec.DMP'
image1 = readDMP(path1)

plt.ion()
plt.figure(figsize=[16, 9])
NumberOfImages = 50
DifferenceVector = np.empty(NumberOfImages + 1)
DifferenceVector[:] = np.nan
print 'Calculation image difference from lowest image in stack N to the', \
    NumberOfImages, 'top images of stack N+1'
plt.subplot(231)
plt.imshow(image1, cmap='gray')
plt.title(os.path.basename(path1))
for image in range(NumberOfImages):
    path2 = '/sls/X02DA/data/e15171/Data10/disk1/Cand2_265_a_B4_/rec_DMP_Paganin_0/Cand2_265_a_B4_' + str(image + 1).zfill(3) + '.rec.DMP'
    image2 = readDMP(path2)
    plt.subplot(232)
    plt.imshow(image2, cmap='gray')
    plt.title(os.path.basename(path2))
    print 'calculating difference for image', os.path.basename(path2)
    DifferenceImage = np.subtract(image1, image2)
    del image2
    DifferenceVector[image] = np.absolute(np.sum(DifferenceImage.flatten()))
    plt.subplot(233)
    if DifferenceVector[image] == np.nanmin(DifferenceVector):
        plt.imshow(DifferenceImage, cmap='gray')
        plt.title(('\n').join(['Current best Difference Image is from',
            os.path.basename(path2)]))
    del DifferenceImage
    plt.subplot(212)
    plt.cla()
    plt.plot(DifferenceVector, 'o-')
    plt.xlim([0, NumberOfImages + 1])
    plt.ylim(ymin=0)
    plt.title('Absolute image difference')
    plt.draw()
    gc.collect()

print
print 'The best matching images are'
print os.path.basename(path1)
print 'and'
print 'TELL ABOUT THE OTHER IMAGE'
