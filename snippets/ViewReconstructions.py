#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ViewReconstructions.py | David Haberthür <david.haberthuer@psi.ch>

This script is best symlinked to each of the diskX subfolders and then run
from there.

    > cd ~/Data10/disk1
    > ln -s ~/beamline-scripts/snippets/ViewReconstructions.py .
    > python ViewReconstructions.py

It goes through all the subfolders, looks for a rec-folder and loads the slice
number set on line 26 into a numpy array for display.
This makes it fairly easy to quickly skim through all the already done
reconstructions and see if there's a problem with them.
"""

import numpy
import matplotlib.pyplot as plt
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
          'start the script again.'
    print 'module load xbl/epd; module load xbl/tifffile/2012.01.01'
    exit()

# Detect all subfolders
print 'Looking for reconstructions in all subfolders of %s' % \
      os.path.abspath(os.getcwd())
CurrentDisk = os.path.basename(os.getcwd())
ReconstructionFolders = glob.glob(os.path.join('/sls/X02DA/Data10/e15423',
                                               CurrentDisk, '*', 'rec_*'))
if not ReconstructionFolders:
    print 'No reconstruction subfolders found.'
    print 'Copy the script to ~/Data10/diskX and start it from there'
    exit()

print 'Showing three slices for each of the %s found reconstruction ' \
      'folders in the subfolder of %s\n' \
      % (len(ReconstructionFolders), CurrentDisk)

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
        print 'Reading three %s files from the %s ones found in %s\n' % (
            Suffix, len(glob.glob(os.path.join(CurrentFolder, '*' + Suffix))),
            CurrentFolder)
        FileTop = sorted(glob.glob(os.path.join(CurrentFolder,
                                                '*.' + Suffix)))[
            len(glob.glob(os.path.join(CurrentFolder, '*.' + Suffix)))/4]
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
                                                 '*.' + Suffix)))/4+1))
        plt.subplot(132)
        plt.imshow(ImageMid, cmap='gray', interpolation='none')
        plt.title('Slice %s' %
                  str(2*len(glob.glob(os.path.join(CurrentFolder,
                                                   '*.' + Suffix)))/4+1))
        plt.subplot(133)
        plt.imshow(ImageBot, cmap='gray', interpolation='none')
        plt.title('Slice %s' %
                  str(3*len(glob.glob(os.path.join(CurrentFolder,
                                                   '*.' + Suffix)))/4+1))
        plt.suptitle('%s/%s: three slices of %s from %s' % (
            counter + 1, len(ReconstructionFolders),
            len(glob.glob(os.path.join(CurrentFolder, '*.' + Suffix))),
            CurrentFolder))
        plt.tight_layout()
        plt.show()
print 'Done'
