#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ViewReconstructions.py | David Haberthür <david.haberthuer@psi.ch>

This script is best symlinked to each of the diskX subfolders and then run
from there. Or you can run it from inside the diskX subfolder with the
absolute path to the snippets directory...

    > cd ~/Data10/disk1
    > ln -s ~/beamline-scripts/snippets/ViewReconstructions.py .
    > python ViewReconstructions.py

It goes through all the subfolders, looks for a rec-folder and loads the slice
number set on line 26 into a numpy array for display.
This makes it fairly easy to quickly skim through all the already done
reconstructions and see if there's a problem with them.
"""

import numpy
from optparse import OptionParser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages  # multipage PDF output
import glob
import os
import imp
dmpreader = imp.load_source('HandleDMP',
                            os.path.join(os.path.expanduser('~'),
                                         'beamline-scripts/postscan/'
                                         'dmp-files/Python/HandleDMPFiles.py'))
try:
    from tifffile import tifffile
except ImportError:
    print 'To use this script, we need to load two modules, the Enthought ' \
          'Python Distribution and the tiff file library.'
    print 'To do so, please enter the command below into the terminal and ' \
          'start the script again.\n'
    print 'module load xbl/epd; module load xbl/tifffile/2012.01.01\n'
    exit()

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
Parser = OptionParser()
Parser.add_option('-p', dest='PDF', default=False, metavar=1,
                  action='store_true',
                  help='Save result to Overview.pdf')
Parser.add_option('-f', dest='filter', type='str', default='*',
                  metavar='somename',
                  help='Only look at samples named like this. '
                       'Default: %default')
(options, Arguments) = Parser.parse_args()

# Detect all subfolders
print 'Looking for reconstructions in all subfolders of %s' % \
      os.path.abspath(os.getcwd())
ReconstructionFolders = sorted(glob.glob(os.path.join(os.getcwd(),
                                         '*' + options.filter + '*', 'rec_*')))

if not ReconstructionFolders:
    print 'No reconstruction subfolders found.'
    print 'Run the script from ~/Data10/diskX!'
    exit()

if options.PDF:
    # Initialize multipage PDF: http://is.gd/yCB4CC
    if not options.filter == '*':
        PDFName = 'Overview_' + options.filter
    else:
        PDFName = 'Overview'
    PDF = PdfPages(os.path.join(os.path.abspath(os.getcwd()),
                                PDFName + '.pdf'))
    print 'Saving image of',
else:
    print 'Showing',
print 'three slices for each of the %s found reconstruction ' \
      'folders in the subfolder of %s\n' \
      % (len(ReconstructionFolders), os.path.basename(os.getcwd()))
if options.PDF:
    print 'All your images are going to a PDF called %s\n' % os.path.join(
        os.path.abspath(os.getcwd()), PDFName)

for counter, CurrentFolder in enumerate(ReconstructionFolders):
    if len(glob.glob(os.path.join(CurrentFolder, '*.DMP'))):
        Suffix = 'DMP'
    elif len(glob.glob(os.path.join(CurrentFolder, '*8bit*'))):
        Suffix = '8bit.tif'
    elif len(glob.glob(os.path.join(CurrentFolder, '*16bit*'))):
        Suffix = '16bit.tif'
    else:
        print 'No image files found in %s' % CurrentFolder
        print 'Maybe this sample is still pending on the cluster...\n'
        Suffix = []

    if Suffix:
        print '%s/%s: Reading three %s files from the %s ones found in %s' % (
            counter + 1, len(ReconstructionFolders), Suffix,
            len(glob.glob(os.path.join(CurrentFolder, '*' + Suffix))),
            CurrentFolder)
        FileTop = sorted(glob.glob(os.path.join(CurrentFolder,
                                                '*.' + Suffix)))[
            len(glob.glob(os.path.join(CurrentFolder, '*.' + Suffix))) / 4]
        FileMid = sorted(glob.glob(os.path.join(CurrentFolder,
                                                '*.' + Suffix)))[
            2 * len(glob.glob(os.path.join(CurrentFolder, '*.' + Suffix))) / 4]
        FileBot = sorted(glob.glob(os.path.join(CurrentFolder,
                                                '*.' + Suffix)))[
            3 * len(glob.glob(os.path.join(CurrentFolder, '*.' + Suffix))) / 4]
        if Suffix == 'DMP':
            ImageTop = dmpreader.readDMP(FileTop)
            ImageMid = dmpreader.readDMP(FileMid)
            ImageBot = dmpreader.readDMP(FileBot)
        else:
            with tifffile(FileTop) as TIFFFile:
                ImageTop = TIFFFile.asarray()
            with tifffile(FileMid) as TIFFFile:
                ImageMid = TIFFFile.asarray()
            with tifffile(FileBot) as TIFFFile:
                ImageBot = TIFFFile.asarray()
        plt.figure(figsize=[20, 9])
        plt.subplot(131)
        plt.imshow(ImageTop, cmap='gray', interpolation='none')
        plt.title('Slice %s' %
                  str(len(glob.glob(os.path.join(CurrentFolder,
                                                 '*.' + Suffix))) / 4 + 1))
        plt.subplot(132)
        plt.imshow(ImageMid, cmap='gray', interpolation='none')
        plt.title('Slice %s' %
                  str(2 * len(glob.glob(os.path.join(CurrentFolder,
                                                     '*.' + Suffix))) / 4 + 1))
        plt.subplot(133)
        plt.imshow(ImageBot, cmap='gray', interpolation='none')
        plt.title('Slice %s' %
                  str(3 * len(glob.glob(os.path.join(CurrentFolder,
                                                     '*.' + Suffix))) / 4 + 1))
        plt.suptitle('%s/%s: three slices of %s from %s' % (
            counter + 1, len(ReconstructionFolders),
            len(glob.glob(os.path.join(CurrentFolder, '*.' + Suffix))),
            CurrentFolder))
        plt.tight_layout()
        if options.PDF:
            print '\tAdding page to %s' % os.path.join(
                os.path.abspath(os.getcwd()), PDFName)
            plt.savefig(PDF, format='pdf')
        plt.show()

if options.PDF:
    print 'Saving the PDF will take a while...'
    print 'Especially if you requested lots of images.'
    PDF.close()
    print 'All your images are now in %s' % os.path.join(
        os.path.abspath(os.getcwd()), PDFName)
print 'Done'
