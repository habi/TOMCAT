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
from optparse import OptionParser
import sys


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


def AskUser(Blurb, Choices):
    """
    Ask for user input.
    """
    print(Blurb)
    for Counter, Item in enumerate(sorted(Choices)):
        print '    * [' + str(Counter) + ']:', Item
    Selection = []
    while Selection not in range(len(Choices)):
        try:
            Selection = int(input(' '.join(['Please enter the choice you',
                                            'want [0-' +
                                            str(len(Choices) - 1) +
                                            ']:'])))
        except:
            print 'You actually have to select *something*'
        if Selection not in range(len(Choices)):
            print 'Try again with a valid choice'
    print 'You selected', sorted(Choices)[Selection]
    return sorted(Choices)[Selection]


def bold(msg):
    """
    Type in bold, from http://is.gd/HCaDv9
    """
    return u'\033[1m%s\033[0m' % msg

# clear the commandline
os.system('clear')

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-D', '--Directory', dest='Directory',
                  help='Location of the *first* subscan of the stack (scan_'
                  'B1)',
                  metavar='path')
parser.add_option('-r', '--Reconstructions', dest='Reconstructions',
                  help='Choose "DMP", "16bit" or "8bit", otherwise we will '
                  'ask',
                  metavar='DMP')
parser.add_option('-v', '--verbose', dest='Verbose',
                  default=False,
                  action='store_true',
                  help='Be really chatty, (Default: %default)',
                  metavar=1)
(options, args) = parser.parse_args()

# Logging
#def myLogger(Folder, LogFileName):
#    """
#    Since logging in a loop does always write to the first instaniated file,
#    we make a little wrapper around the logger function to write to a defined
#    log file.
#    Based on http://stackoverflow.com/a/2754216/323100
#    """
#    import logging
#    import os
#    logger = logging.getLogger(LogFileName)
#    # either set INFO or DEBUG
#    #~ logger.setLevel(logging.DEBUG)
#    logger.setLevel(logging.INFO)
#    handler = logging.FileHandler(os.path.join(Folder, LogFileName), 'w')
#    logger.addHandler(handler)
#    return logger

options.Directory = '/sls/X02DA/data/e15171/Data10/disk1/fish1b_A_z265_B1_'
options.Directory = '/sls/X02DA/data/e15171/Data10/disk1/Cand2_265_a_B1_'

# show the help if necessary parameters are missing
if options.Directory is None:
    parser.print_help()
    print 'Example:'
    print 'The command below does THIS AND THAT'
    print ''
    print sys.argv[0], '-D /sls/X02DA/data/e12740/Data10/disk1/SampleName_B1'
    print ''
    sys.exit(1)

Folder = os.path.dirname(options.Directory)
SampleBaseName = os.path.basename(options.Directory).replace('_B1_', '')

# Find number of stacks that were scanned
print 'Looking for all stacked scans of', bold(SampleBaseName), 'in', \
    bold(Folder)
print
NumberOfStacks = 1
while os.path.exists(os.path.join(Folder,
                                   SampleBaseName + '_B' +
                                   str(NumberOfStacks) + '_/')):
    NumberOfStacks += 1
    print 'I found', os.path.basename(os.path.join(Folder,
                                                  SampleBaseName + '_B' +
                                                  str(NumberOfStacks)))

print
print 'We thus have', NumberOfStacks, 'stacked scans to go through.'
print

# Grab directory of reconstructions.
# Account that there might be multiple ones
print 'Looking for folders with reconstructions in', \
    bold(os.path.basename(options.Directory))
RecDirectories = glob.glob(os.path.join(options.Directory, '*rec*'))
RecDirectories = [ os.path.basename(folder) for folder in RecDirectories]
if len(RecDirectories) > 1:
    print 'I found multiple directories with reconstructions.',
    RecDirectory = AskUser('Which one shall I use?', RecDirectories)
else:
    print 'I only found one rec folder'
    RecDirectory = RecDirectories[0]
print 'Working with the reconstructions in the rec folder', \
    bold(os.path.basename(RecDirectory))

# Decide what to do
if 'DMP' in RecDirectory:
    options.Reconstructions = 'DMP'
elif '16' in RecDirectory:
    options.Reconstructions = '8bit'
elif '8' in RecDirectory:
    options.Reconstructions = '16bit'

if options.Reconstructions is not 'DMP':
    sys.exit('Not implemented yet, please choose DMP')

#~ import sys
#~ total = 10
#~ for i in range(total):
    #~ sys.stdout.write('%d / %d\r' % (i, total))
    #~ sys.stdout.flush()
#~ print('\nDone')

for CurrentStack in range(NumberOfStacks):
    TopStack = SampleBaseName + '_B' + str(CurrentStack) + '_'
    BottomStack = SampleBaseName + '_B' + str(CurrentStack + 1) + '_'
    print 80 * '-'
    print 'Comparing bottom of stack', bold(TopStack), 'with top of stack', \
        bold(BottomStack)

exit()

path1 = '/sls/X02DA/data/e15171/Data10/disk1/Cand2_265_a_B3_/rec_DMP_Paganin_0/Cand2_265_a_B3_399.rec.DMP'
BottomImage = readDMP(path1)

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
