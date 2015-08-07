#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ComputeSNR.py | David Haberthür <david.haberthuer@psi.ch>

This script can be used to calculate and plot the Signal to noise ratio of an
image
"""

from optparse import OptionParser
import matplotlib.pyplot as plt
import numpy
import scipy.stats

plt.ion()

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-f', '--file', dest='Filename',
                  help='Filename of the image to compute the SNR',
                  metavar='path')
parser.add_option('-r', '--roi', dest='ROI',
                  help='ROI to calculate the SNR from '
                       '[Upperleft X,Y,Lowerright X,Y]. If no ROI is given, '
                       'the user has to define a ROI on the image with the '
                       'mouse.', metavar='10,100,400,550')
parser.add_option('-c', '--cnrroi', dest='CNRCoordinates',
                  help='Coordinates of two points to calculate the CNR '
                       'inbetweeen [First X,Y,Second X,Y]. If no Coordinates '
                       'are given, the user is asked to input them by mouse.',
                  metavar='150,30,150,80')
parser.add_option('-w', '--width', dest='CNRPixelWidth', type=int, default=5,
                  help='ROI around the clicked point to add for CNR '
                       'calculation (±value)', metavar='6')
(options, args) = parser.parse_args()

if options.ROI:
    # make the ROI-Coordinates into a double tuple, so we can use less code
    # afterwards
    options.ROI = ((int(options.ROI.split(',')[0]),
                   int(options.ROI.split(',')[1])),
                   (int(options.ROI.split(',')[2]),
                   int(options.ROI.split(',')[3])))
if options.CNRCoordinates:
    # make the CNRCoordinates into a double tuple, so we can use less code
    # afterwards
    options.CNRCoordinates = ((int(options.CNRCoordinates.split(',')[0]),
                              int(options.CNRCoordinates.split(',')[1])),
                              (int(options.CNRCoordinates.split(',')[2]),
                              int(options.CNRCoordinates.split(',')[3])))

# show the help if no parameters are given
if options.Filename is None:
    parser.print_help()
    print 'Example:'
    print 'The command below calculates the SNR of the region ' \
          '(300,200,650,450) of "tomcat.jpg".'
    print 'Afterwards, the CNR of the coordinates (213,128) and (285,230)'
    print 'is calculated in a 100 px big square (±5 px) around them.'
    print
    print 'ComputeSNR.py -f tomcat.jpg -r 300,200,650,450 ' \
          '-c 213,128,285,230 -w 5'
    print
    exit(1)

# Read File
print 'Reading "' + options.Filename + '"...'
try:
    Image = plt.imread(options.Filename)
    # sum RGB channels, i.e. convert to grayscale
    Image = sum(Image, axis=2)
    # Flip the image upsidedown, since Matplotlib set the origin differently
    Image = numpy.flipud(Image)
except IOError:
    print 'I was not able to read the file, did you specify the correct' \
          'path with "-f"?'
    exit(1)
print options.Filename, 'is', Image.shape[1], 'x', Image.shape[0],\
    'pixels big.'

# Show Image
plt.figure(1)
plt.subplot(121)
plt.imshow(Image, cmap='gray', interpolation='nearest')
if options.ROI is None:
    plt.title('Please select the two corners of the ROI to work with')
    options.ROI = plt.ginput(2)
plt.hlines(options.ROI[0][1], options.ROI[0][0], options.ROI[1][0], 'r',
           linewidth=3)
plt.hlines(options.ROI[1][1], options.ROI[0][0], options.ROI[1][0], 'r',
           linewidth=3)
plt.vlines(options.ROI[0][0], options.ROI[0][1], options.ROI[1][1], 'r',
           linewidth=3)
plt.vlines(options.ROI[1][0], options.ROI[0][1], options.ROI[1][1], 'r',
           linewidth=3)
x1 = int(round(options.ROI[0][0]))
y1 = int(round(options.ROI[0][1]))
x2 = int(round(options.ROI[1][0]))
y2 = int(round(options.ROI[1][1]))
print 'We are calculating the SNR in the ROI for x=' + str(x1) + ':' + \
      str(x2) + ' and y=' + str(y1) + ':' + str(y2) + '.'
plt.title('Original')
plt.draw()

# # Show new figure with ROI
# plt.figure(2)
# plt.subplot(132)
# plt.imshow(Image[y1:y2, x1:x2], cmap='gray',interpolation='nearest')
# PlotTitle = 'ROI from x=' + str(x1) + ' to ' + str(x2) + ' and from y=' + \
#     str(y1) + ' to ' + str(y2)
# plt.title(PlotTitle)
# plt.draw()

# Select points for CNR
# plt.figure(3)
plt.subplot(122)
plt.imshow(Image[y1:y2, x1:x2], cmap='gray', interpolation='nearest')
if options.CNRCoordinates is None:
    plt.title('Pick two points to calculate the CNR between them')
    options.CNRCoordinates = plt.ginput(2)
plt.draw()
# draw CNR ROI around them
# Point 1
plt.hlines(options.CNRCoordinates[0][1] - options.CNRPixelWidth,
           options.CNRCoordinates[0][0] - options.CNRPixelWidth,
           options.CNRCoordinates[0][0] + options.CNRPixelWidth, 'r')
plt.hlines(options.CNRCoordinates[0][1] + options.CNRPixelWidth,
           options.CNRCoordinates[0][0] - options.CNRPixelWidth,
           options.CNRCoordinates[0][0] + options.CNRPixelWidth, 'r')
plt.vlines(options.CNRCoordinates[0][0] - options.CNRPixelWidth,
           options.CNRCoordinates[0][1] - options.CNRPixelWidth,
           options.CNRCoordinates[0][1] + options.CNRPixelWidth, 'r')
plt.vlines(options.CNRCoordinates[0][0] + options.CNRPixelWidth,
           options.CNRCoordinates[0][1] - options.CNRPixelWidth,
           options.CNRCoordinates[0][1] + options.CNRPixelWidth, 'r')
# Point 2
plt.hlines(options.CNRCoordinates[1][1] - options.CNRPixelWidth,
           options.CNRCoordinates[1][0] - options.CNRPixelWidth,
           options.CNRCoordinates[1][0] + options.CNRPixelWidth, 'r')
plt.hlines(options.CNRCoordinates[1][1] + options.CNRPixelWidth,
           options.CNRCoordinates[1][0] - options.CNRPixelWidth,
           options.CNRCoordinates[1][0] + options.CNRPixelWidth, 'r')
plt.vlines(options.CNRCoordinates[1][0] - options.CNRPixelWidth,
           options.CNRCoordinates[1][1] - options.CNRPixelWidth,
           options.CNRCoordinates[1][1] + options.CNRPixelWidth, 'r')
plt.vlines(options.CNRCoordinates[1][0] + options.CNRPixelWidth,
           options.CNRCoordinates[1][1] - options.CNRPixelWidth,
           options.CNRCoordinates[1][1] + options.CNRPixelWidth, 'r')
plt.draw()

S1 = numpy.mean(Image[options.CNRCoordinates[0][1] -
                      options.CNRPixelWidth:options.CNRCoordinates[0][1] +
                      options.CNRPixelWidth,
                      options.CNRCoordinates[0][0] -
                      options.CNRPixelWidth:options.CNRCoordinates[0][0] +
                      options.CNRPixelWidth])
S2 = numpy.mean(Image[options.CNRCoordinates[1][1] -
                      options.CNRPixelWidth:options.CNRCoordinates[1][1] +
                      options.CNRPixelWidth,
                      options.CNRCoordinates[1][0] -
                      options.CNRPixelWidth:options.CNRCoordinates[1][0] +
                      options.CNRPixelWidth])
Sigma1 = numpy.std(Image[options.CNRCoordinates[0][1] -
                         options.CNRPixelWidth:options.CNRCoordinates[0][1] +
                         options.CNRPixelWidth,
                         options.CNRCoordinates[0][0] -
                         options.CNRPixelWidth:options.CNRCoordinates[0][0] +
                         options.CNRPixelWidth])
Sigma2 = numpy.std(Image[options.CNRCoordinates[1][1] -
                         options.CNRPixelWidth:options.CNRCoordinates[1][1] +
                         options.CNRPixelWidth,
                         options.CNRCoordinates[1][0] -
                         options.CNRPixelWidth:options.CNRCoordinates[1][0] +
                         options.CNRPixelWidth])

# Output
print
print '---'
print 'ROI:'
SNR = scipy.stats.signaltonoise(Image[y1:y2, x1:x2].ravel())
Mean = numpy.mean(Image[y1:y2, x1:x2])
STD = numpy.std(Image[y1:y2, x1:x2])
print 'The SNR of the ROI is:', SNR
print 'Mean =', round(Mean, 3), '| STD =', round(STD, 3),\
    '| SNR ("Mean/STD") =', round(Mean / STD, 3)

print
print 'CNR between the two selected points:'
print 'with a ROI area around them of', (2 * options.CNRPixelWidth) ** 2,\
    'pixels (±width of', options.CNRPixelWidth, 'pixels).'

CNR = numpy.abs(S1 - S2) / (Sigma1 + Sigma2)
print 'The CNR between the two points is:', CNR
title = 'CNR: ' + str(round(CNR, 4))
plt.title(title)
plt.draw()

plt.ioff()

plt.show()
