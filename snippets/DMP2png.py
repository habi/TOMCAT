#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DMP2png.py | David Haberthür <david.haberthuer@psi.ch>

This script expects the path to a DMP file as only parameter and converts it to
a PNG file in the same directory.
"""

import sys
import os
import numpy
from scipy import misc


def readDMP(filename):
    """
    Opens and reads DMP file.
    Returns a numpy ndarray which can be displayed/written/handled further.
    """
    # Open the file
    dmpfile = open(filename, 'rb')
    # The DMP file format is a very simple file format; the header consists of
    # 3 unsigned 16bit integers specifying the image dimensions, followed by a
    # stream of 32-bit floats in little-endian byte order.
    # Load Header.  It's first two values are the image size.
    header = numpy.fromfile(dmpfile, numpy.int16, 3)
    imageSize = (header[1], header[0])
    # Load file and reshape to the size from the header
    image = numpy.fromfile(dmpfile, numpy.float32)
    image = image.reshape(imageSize)
    dmpfile.close()
    return image

# Get DMP file name, read it in and write it out as JPG
DMPFileName = sys.argv[1]
Image = readDMP(DMPFileName)
misc.imsave(os.path.splitext(os.path.abspath(DMPFileName))[0] + '.png', Image)
