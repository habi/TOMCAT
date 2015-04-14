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
try:
    from tifffile import tifffile
except ImportError:
    print 'To use this script, you need to load two modules'
    print 'Use the commands below to do this:'
    print '   module load xbl/epd'
    print '   module load xbl/tifffile/2012.01.01'
    exit()

CurrentDisk = os.path.basename(os.getcwd())
Slice = 1280
print 'Looking for reconstructions in all subfolders of %s' % CurrentDisk

Reconstructions = glob.glob(os.path.join('/sls/X02DA/Data10/e15423',
                                         CurrentDisk, '*', 'rec_*',
                                         '*' + str(Slice) + '*'))

print 'Showing slice %s of each rec_* folder' % Slice

for counter, FileName in enumerate(Reconstructions):
    print 'Reconstruction %s of %s: %s' % (counter + 1,
                                           len(Reconstructions),
                                           os.path.basename(FileName))
    with tifffile(FileName) as TIFFFile:
        Image = TIFFFile.asarray()
    plt.figure(figsize=[12, 12])
    plt.imshow(Image, cmap='gray')
    plt.title(os.path.basename(FileName) + ' from ' +
              os.path.dirname(FileName))
    plt.tight_layout()
    plt.show()
