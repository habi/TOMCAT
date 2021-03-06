#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
StackedScanOverlapFinder.py | David Haberthür <david.haberthuer@psi.ch>

Script to find the best "overlap" from merged scans.
Even when setting the overlap to a certain value (-c 1.1 in stacked-scan.py),
the overlap might not be exactly the given one.
If one wants to merge all the subscans to a merged dataset this script can help
with finding the best match between the reconstructed slices.
It does this by loading the lowest image from stack N and calculating the
mean square errorto the options.Percent top images from stack N+1.
"""

from __future__ import division
import platform
import os
import glob
from optparse import OptionParser
import numpy
import time
import gc
import sys
import matplotlib
import matplotlib.pyplot as plt

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
parser.add_option('-o', '--Offset', dest='Offset',
                  help='Do not use the bottom/last slice, but the one with '
                  'this offset. (Default: %default)',
                  metavar='7', type=int, default=0)
parser.add_option('-v', '--verbose', dest='Verbose',
                  default=False,
                  action='store_true',
                  help='Be really chatty, (Default: %default)',
                  metavar=1)
(options, args) = parser.parse_args()


# Define handy functions
def readDMP(filename):
    """
    Opens and reads DMP file.
    Returns numpy ndarray.
    From Martin Nyvlts DMP reader, available on
    intranet.psi.ch/wiki/bin/viewauth/Tomcat/BeamlineManual#The_DMP_file_format
    """
    fd = open(filename, 'rb')
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
        except NameError:
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


def myLogger(Folder, LogFileName, verbose=options.Verbose):
    """
    Since logging in a loop does always write to the first instaniated file,
    we make a little wrapper around the logger function to write to a defined
    log file.
    Based on http://stackoverflow.com/a/2754216/323100
    """
    import logging
    logger = logging.getLogger(LogFileName)
    # either set INFO or DEBUG
    # logger.setLevel(logging.DEBUG)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(Folder, LogFileName), 'w')
    logger.addHandler(handler)
    if verbose:
        print 'Logging to', os.path.join(Folder, LogFileName)
    return logger


def normalizeimage(img, depth=1, verbose=options.Verbose):
    """Normalize image to chosen bit depth"""
    if verbose:
        print 'Normalizing input image from [' + str(numpy.min(img)) + ':' +\
              str(numpy.max(img)) + '] to',
    normalizedimage = ((img - numpy.min(img)) * (depth / (numpy.max(img) -
                                                          numpy.min(img))))
    if verbose:
        print '[' + str(numpy.min(normalizedimage)) + ':' +\
              str(numpy.max(normalizedimage)) + ']'
    return normalizedimage

# Show the help (-h) if necessary parameter (-D) is missing
if options.Directory is None:
    parser.print_help()
    print 'Example:'
    print 'The command below calculates the overlap of all the stacked', \
        'scans of sample', bold('SampleName'), 'for an overlap of 11% (give',\
        'the script a bigger overlap that what you expect) and is really', \
        'chatty about it.'
    print ''
    print sys.argv[0], '-D /sls/X02DA/data/e12740/Data10/disk1/', \
        'SampleName_B1 -p 11 -v'
    print ''
    sys.exit(1)

# Make sure we are running a good version of matplotlib (i.e. > 1)
if float(str(matplotlib.__version__)[:3]) < 1:
    print '\nWe are running matplotlib version', matplotlib.__version__, 'on', \
        platform.node()
    print 'To make this script work, we need a matplotlib version > 1.'
    print 'To load such a version, please enter the following command in', \
        'the terminal  and restart the script.'
    print '\n\tmodule load xbl/epd_free/7.3-2-2013.06\n'
    sys.exit()

# clear the commandline
os.system('clear')

# All systems GO!
StartingFolder = os.path.dirname(os.path.abspath(options.Directory))
SampleBaseName = os.path.basename(os.path.abspath(options.Directory)).replace(
    '_B1', '_B*')
# Find number of stacks that were scanned
print 'Looking for all stacked scans of', bold(SampleBaseName), 'in', \
    bold(StartingFolder)
StackList = sorted(glob.glob(os.path.join(StartingFolder,
                                          SampleBaseName + '*')))
if options.Verbose:
    print 'I found'
    for i in StackList:
        print '\t', i
NumberOfStacks = len(StackList)
print 'Found a total of', NumberOfStacks, 'stacked scans to go through.'

# See what kind of images we should load
if not options.Reconstructions:
    # Grab directory of reconstructions.
    # Account for the case that there might be multiple ones
    if options.Verbose:
        print 'Looking for folders with reconstructions in', \
            bold(os.path.basename(options.Directory))
    RecDirectories = glob.glob(os.path.join(options.Directory, 'rec*'))
    RecDirectories = [os.path.basename(folder) for folder in RecDirectories]
    print 80 * '-'
    if len(RecDirectories) > 1:
        print 'I found multiple directories with reconstructions.',
        RecDirectory = AskUser('Which one shall I use?', RecDirectories)
    else:
        if options.Verbose:
            print 'I found only one rec folder, using that one.'
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
else:
    RecDirectory = os.path.basename(glob.glob(os.path.join(
        options.Directory, '*' + options.Reconstructions + '*'))[0])
    # add '.tif' for 8 or 16 bit case, so we can easily generate the filename
    if 'DMP' not in options.Reconstructions:
        options.Reconstructions += '.tif'
print 80 * '-'

# Count number of files in rec folder
# TODO: parse logfile instead of just counting files
NumberOfReconstructions = len(glob.glob(os.path.join(StackList[0],
                              RecDirectory, '*.' + options.Reconstructions)))
# Find out how many zeroes we have to add
ZeroFilling = len(str(NumberOfReconstructions))
print 'We found', NumberOfReconstructions,\
    'reconstructions in the rec folder of the first stack.'
print 'We will check the top', \
    str(int(NumberOfReconstructions * options.Percent / 100)), \
    'images (' + str(options.Percent), '%) of the scan N+1 with the',
if options.Offset:
    print 'image "bottom - %s" of stack N.' % options.Offset
else:
    print 'bottom image of stack N.'

# Go through the stack list
for StackNumber, Stack in enumerate(StackList[:-1]):
    # Generate file names
    TopStack = os.path.join(StackList[StackNumber], RecDirectory)
    BottomStack = os.path.join(StackList[StackNumber + 1], RecDirectory)
    # Inform user
    print 80 * '-'
    if options.Offset:
        print 'Comparing "bottom - %s" of stack.' % options.Offset,
    else:
        print 'Comparing bottom of stack',
    print bold(os.path.basename(os.path.dirname(TopStack))), \
        'with top of stack', \
        bold(os.path.basename(os.path.dirname(BottomStack)))
    # Set up logging and write log file header
    LogFileName = '_stackedscan.merge.' + \
        os.path.basename(os.path.dirname(TopStack)) + '.' + \
        os.path.basename(os.path.dirname(BottomStack)) + '.log'
    try:
        logfile = myLogger(BottomStack, LogFileName)
    except:
        print 'Cannot write to', os.path.join(BottomStack, LogFileName)
        print 'Does its directory exist?'
        sys.exit(1)
    logfile.info('Log file for stacked scan merging, performed on %s',
                 time.strftime('%d.%m.%Y at %H:%M:%S'))
    logfile.info(80 * '-')
    logfile.info('Comparing the stacks')
    logfile.info('\t-' + TopStack)
    logfile.info('\t-' + BottomStack)
    logfile.info('with each other')
    logfile.info(80 * '-')
    # Read bottom image from top stack
    TopStackImageFilename = os.path.join(TopStack,
                                         os.path.basename(os.path.dirname(
                                             TopStack)) +
                                         str(NumberOfReconstructions -
                                             options.Offset) + '.rec.' +
                                         options.Reconstructions)
    if 'DMP' in options.Reconstructions:
        TopStackImage = readDMP(TopStackImageFilename)
    else:
        TopStackImage = normalizeimage(plt.imread(TopStackImageFilename))
    logfile.info('Comparing ' + os.path.basename(TopStackImageFilename))
    # Prepare image display
    plt.ion()
    plt.figure(figsize=[16, 9])
    plt.suptitle('Comparing "%s" of %s with ../%s' % (RecDirectory,
                 os.path.dirname(TopStack),
                 os.path.basename(os.path.dirname(BottomStack))))
    MeanSquareErrorVector = numpy.empty(NumberOfReconstructions + 1)
    MeanSquareErrorVector[:] = numpy.nan
    # Show image we compare all the images to
    plt.subplot(231)
    plt.imshow(TopStackImage, cmap='gray')
    plt.title(os.path.basename(TopStackImageFilename))
    NumberOfImagesToCheck = NumberOfReconstructions * options.Percent / 100
    # Go through each image to compare from bottom stack
    for image in range(1, int(NumberOfImagesToCheck)):
        CompareImageFilename = os.path.join(BottomStack,
                                            os.path.basename(
                                                os.path.dirname(BottomStack)) +
                                            str(image).zfill(ZeroFilling) +
                                            '.rec.' + options.Reconstructions)
        if 'DMP' in options.Reconstructions:
            CompareImage = readDMP(CompareImageFilename)
        else:
            CompareImage = normalizeimage(plt.imread(CompareImageFilename))
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
                     ' gives a mean square error of %e' %
                     MeanSquareErrorVector[image])
        # Show image with the currently lowest MSE
        plt.subplot(233)
        if MeanSquareErrorVector[image] == numpy.nanmin(MeanSquareErrorVector):
            plt.imshow(DifferenceImage, cmap='gray')
            plt.title('\n'.join([
                'Current lowest MSE (%.3e) is from' % numpy.nanmin(
                    MeanSquareErrorVector),
                os.path.basename(CompareImageFilename)]))
            CurrentBestImageName = os.path.basename(CompareImageFilename)
        # Show plot with found differences
        plt.subplot(212)
        plt.cla()
        plt.plot(MeanSquareErrorVector, linestyle='-', marker='None',
                 color='b')
        plt.plot(numpy.ndarray.tolist(MeanSquareErrorVector).index(
            numpy.nanmin(MeanSquareErrorVector)), numpy.nanmin(
            MeanSquareErrorVector), marker='o', color='b')
        plt.xlim([1, NumberOfImagesToCheck])
        plt.ylim(ymin=0)
        plt.ylabel('Mean square error')
        plt.xlabel('Image to check')
        CurrentTitle = 'Checking image', str(image), 'of', \
            str(int(NumberOfImagesToCheck)), '(current best at image', \
            str(numpy.ndarray.tolist(MeanSquareErrorVector).index(
                numpy.nanmin(MeanSquareErrorVector))) + ')'
        plt.title(' '.join(CurrentTitle))
        plt.draw()
        # Try to save some memory
        del CompareImage
        del DifferenceImage
        gc.collect()
        if options.Verbose:
            print '%3d/%d: Current lowest MSE (%.1e) from ' \
                  '%s\r' % (image, NumberOfImagesToCheck,
                            numpy.nanmin(MeanSquareErrorVector),
                            CurrentBestImageName)
        else:
            # Clean command-line with "\r" & "flush". From http://is.gd/HCaDv9
            sys.stdout.write('%3d/%d: Current lowest MSE (%.1e) from %s\r' % (
                image, NumberOfImagesToCheck,
                numpy.nanmin(MeanSquareErrorVector), CurrentBestImageName))
            sys.stdout.flush()
    # Prepare output figure
    OutputFigureName = os.path.join(BottomStack,
                                    '_stackedscan.difference.' +
                                    os.path.basename(os.path.dirname(
                                        TopStack)) + '.' +
                                    os.path.basename(os.path.dirname(
                                        BottomStack)) + '.png')
    plt.savefig(OutputFigureName, transparent='True')
    plt.close()
    # Tell and log which file is best
    # Convert array to list so we can use ".index()" to find the image number
    BestMatchingImageNmbr = numpy.ndarray.tolist(
        MeanSquareErrorVector).index(numpy.nanmin(MeanSquareErrorVector))
    BestMatchingImageFilename = os.path.join(BottomStack,
                                             os.path.basename(
                                                 os.path.dirname(
                                                     BottomStack)) +
                                             str(BestMatchingImageNmbr).zfill(
                                                 ZeroFilling) + '.rec.' +
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
    print 'Image saved to', OutputFigureName
    print 'Logfile written to', LogFileName

print 80 * '-'
print 'Done with everything'
