"""
Script to find the best "overlap" from merged scans.
Even when setting the overlap to a certain value (-c 1.1 in stacked-scan.py),
the overlap might not be exactly the given one.
If one wants to merge all the subscans to a merged dataset this script can help
with finding the best match between the reconstructed slices.
It does this by loading the lowest image from stack N and calculating the
mean square errorto the options.Percent top images from stack N+1.
"""

from __future__ import division
import glob
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy
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

    headerData = numpy.fromfile(fd, datatype, numberOfHeaderValues)

    imageShape = (headerData[1], headerData[0])

    imageData = numpy.fromfile(fd, numpy.float32, -1)
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
parser.add_option('-p', '--Percent', dest='Percent',
                  help='How many percent of stack N+1 should we compare with '
                  'the last image of stack N. (Default: %default %)',
                  metavar='14', type=int, default=10)
parser.add_option('-v', '--verbose', dest='Verbose',
                  default=False,
                  action='store_true',
                  help='Be really chatty, (Default: %default)',
                  metavar=1)
(options, args) = parser.parse_args()


def myLogger(Folder, LogFileName):
    """
    Since logging in a loop does always write to the first instaniated file,
    we make a little wrapper around the logger function to write to a defined
    log file.
    Based on http://stackoverflow.com/a/2754216/323100
    """
    import logging
    import os
    logger = logging.getLogger(LogFileName)
    # either set INFO or DEBUG
    #~ logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(Folder, LogFileName), 'w')
    logger.addHandler(handler)
    return logger

#~ options.Directory = '/sls/X02DA/data/e15171/Data10/disk1/fish1b_A_z265_B1_'
#~ options.Directory = '/sls/X02DA/data/e15171/Data10/disk1/Cand2_265_a_B1_'

# show the help if necessary parameters are missing
if options.Directory is None:
    parser.print_help()
    print 'Example:'
    print 'The command below does THIS AND THAT'
    print ''
    print sys.argv[0], '-D /sls/X02DA/data/e12740/Data10/disk1/SampleName_B1'
    print ''
    sys.exit(1)

Folder = os.path.dirname(os.path.abspath(options.Directory))
SampleBaseName = os.path.basename(options.Directory).replace('_B1_', '')

# Find number of stacks that were scanned
print 'Looking for all stacked scans of', bold(SampleBaseName), 'in', \
    bold(Folder)
NumberOfStacks = 1
while os.path.exists(os.path.join(Folder,
                                   SampleBaseName + '_B' +
                                   str(NumberOfStacks + 1) + '_/')):
    NumberOfStacks += 1
    if options.Verbose:
        print
        print 'I also found', os.path.basename(os.path.join(Folder,
            SampleBaseName + '_B' + str(NumberOfStacks)))
        print
print 'Found a total of', NumberOfStacks, 'stacked scans to go through.'
print

# Grab directory of reconstructions.
# Account for the case that there might be multiple ones
if options.Verbose:
    print 'Looking for folders with reconstructions in', \
        bold(os.path.basename(options.Directory))
RecDirectories = glob.glob(os.path.join(options.Directory, '*rec*'))
RecDirectories = [os.path.basename(folder) for folder in RecDirectories]
if len(RecDirectories) > 1:
    print 'I found multiple directories with reconstructions.',
    RecDirectory = AskUser('Which one shall I use?', RecDirectories)
else:
    if options.Verbose:
        print 'I only found one rec folder'
    RecDirectory = RecDirectories[0]
print 'Working with the reconstructions in the rec folder', \
    bold(os.path.basename(RecDirectory))

# Decide what to do
if 'DMP' in RecDirectory:
    options.Reconstructions = 'DMP'
elif '16' in RecDirectory:
    options.Reconstructions = '16bit.tif'
elif '8' in RecDirectory:
    options.Reconstructions = '8bit.tif'

if options.Reconstructions is not 'DMP':
    print 'Working with', options.Reconstructions, \
        'images is not implemented yet, please choose a DMP folder'
    # TODO: Implement reading of TIF files
    sys.exit(1)

# Count number of files in rec folder
# TODO: parse logfile instead of counting files
for CurrentStack in range(1, NumberOfStacks):
    Stack = os.path.join(os.path.dirname(options.Directory),
        SampleBaseName + '_B' + str(CurrentStack) + '_', RecDirectory)
NumberOfReconstructions = len(glob.glob(os.path.join(Stack,
    '*.' + options.Reconstructions)))
print 'We found', NumberOfReconstructions, \
    'reconstructions in the rec folder of the first stack.'
print 'We will check the top', \
    str(int(NumberOfReconstructions * options.Percent / 100)), \
    'images (' + str(options.Percent) + \
    '%) of the scan N+1 with the bottom image of stack N.'

for StackNumber in range(1, NumberOfStacks):
    TopStack = os.path.join(os.path.dirname(options.Directory),
        SampleBaseName + '_B' + str(StackNumber) + '_', RecDirectory)
    BottomStack = os.path.join(os.path.dirname(options.Directory),
        SampleBaseName + '_B' + str(StackNumber + 1) + '_', RecDirectory)
    print 80 * '-'
    print 'Comparing bottom of stack', \
        bold(os.path.basename(os.path.dirname(TopStack))), \
        'with top of stack', \
        bold(os.path.basename(os.path.dirname(BottomStack)))
    try:
        logfile = myLogger(BottomStack,
            '_stackedscan.merge.B' + str(StackNumber) + '.B' +
            str(StackNumber + 1) + '.log')
    except:
        print 'Cannot write to', os.path.join(BottomStack,
            '_stackedscan.merge.B' + str(StackNumber) + '.B' +
            str(StackNumber + 1) + '.log')
        print 'Does its directory exist?'
        sys.exit(1)
    logfile.info('Log file for stacked scan merging, performed on %s',
        time.strftime('%d.%m.%Y at %H:%M:%S'))
    logfile.info(80 * '-')
    TopStackImageFilename = os.path.join(TopStack,
        SampleBaseName + '_B' + str(StackNumber) + '_' +
        str(NumberOfReconstructions) + '.rec.' + options.Reconstructions)
    TopStackImage = readDMP(TopStackImageFilename)
    logfile.info('Comparing ' + os.path.basename(TopStackImageFilename))

    # Prepare image display
    plt.ion()
    plt.figure(figsize=[16, 9])
    MeanSquareErrorVector = numpy.empty(NumberOfReconstructions + 1)
    MeanSquareErrorVector[:] = numpy.nan
    # Show image we compare all the images to
    plt.subplot(231)
    plt.imshow(TopStackImage, cmap='gray')
    plt.title(os.path.basename(TopStackImageFilename))
    NumberOfImagesToCheck = NumberOfReconstructions * options.Percent / 100
    # Go through each image to compare
    for image in range(1, int(NumberOfImagesToCheck)):
        CompareImageFilename = os.path.join(BottomStack,
            SampleBaseName + '_B' + str(StackNumber + 1) + '_' +
            str(image).zfill(3) + '.rec.' + options.Reconstructions)
        CompareImage = readDMP(CompareImageFilename)
        # Show current image to compare
        plt.subplot(232)
        plt.imshow(CompareImage, cmap='gray')
        plt.title(os.path.basename(CompareImageFilename))
        # Calculate difference between the given images to show later
        DifferenceImage = numpy.subtract(TopStackImage, CompareImage)
        # Calculate the mean square error
        MeanSquareErrorVector[image] = (DifferenceImage ** 2).mean()
        # Log findings
        logfile.info('with ' + os.path.basename(CompareImageFilename) +
            ' gives a mean square error of %e' % MeanSquareErrorVector[image])
        # Show image with the currently least difference
        plt.subplot(233)
        if MeanSquareErrorVector[image] == numpy.nanmin(MeanSquareErrorVector):
            plt.imshow(DifferenceImage, cmap='gray')
            plt.title(('\n').join([
                'Current best MSE (%.3e) is from' % numpy.nanmin(
                    MeanSquareErrorVector),
                os.path.basename(CompareImageFilename)]))

        # Show plot with found differences
        plt.subplot(212)
        plt.cla()
        plt.plot(MeanSquareErrorVector, '-o')
        plt.xlim([1, NumberOfImagesToCheck])
        plt.ylim(ymin=0)
        plt.ylabel('Mean square error')
        plt.xlabel('Image to check')
        CurrentTitle = 'Checking image', str(image), 'of', \
            str(int(NumberOfImagesToCheck))
        plt.title(' '.join(CurrentTitle))
        plt.draw()
        # Try to save some memory
        del CompareImage
        del DifferenceImage
        gc.collect()
        # Clean command-line with "\r" and "flush". From http://is.gd/HCaDv9
        sys.stdout.write('%d/%d: Current best MSE (%.1e) from %s\r' % (image,
            NumberOfImagesToCheck, numpy.nanmin(MeanSquareErrorVector),
            os.path.basename(CompareImageFilename)))
        sys.stdout.flush()
    plt.savefig(os.path.join(BottomStack,
        '_stackedscan.difference.B' + str(StackNumber) + '.B' +
        str(StackNumber + 1) + '.png'), transparent='True')
    plt.close()
    # Tell and log which file is best
    # Convert array to list so we can use ".index()" to find the image number
    BestMatchingImageNumber = numpy.ndarray.tolist(
        MeanSquareErrorVector).index(numpy.nanmin(MeanSquareErrorVector))
    BestMatchingImageFilename = os.path.join(BottomStack,
            SampleBaseName + '_B' + str(StackNumber + 1) + '_' +
            str(BestMatchingImageNumber).zfill(3) + '.rec.' +
            options.Reconstructions)
    print 'Best match between images', \
        bold(os.path.basename(TopStackImageFilename)), 'and', \
        bold(os.path.basename(BestMatchingImageFilename)), \
        'with a mean square error of %.3e' % numpy.nanmin(
            MeanSquareErrorVector)
    logfile.info(80 * '-')
    logfile.info('Best match between ' +
        os.path.basename(TopStackImageFilename) + ' and ' +
        os.path.basename(BestMatchingImageFilename) +
        ' with a mean square error of %e' % numpy.nanmin(
            MeanSquareErrorVector))
    print 'Log file written to', os.path.join(BottomStack,
            '_stackedscan.merge.B' + str(StackNumber) + '.B' +
            str(StackNumber + 1) + '.log')
    print 'Image saved to to', os.path.join(BottomStack,
        '_stackedscan.difference.B' + str(StackNumber) + '.B' +
        str(StackNumber + 1) + '.png')

print 80 * '-'
print 'Done with everything'
