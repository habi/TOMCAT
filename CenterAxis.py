#!/usr/bin/python

'''
Script to calculate the center for the rotation axis.
Should evolve in an automated centering script.
'''

import sys
from optparse import OptionParser

# Setup the different options for the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-l', '--left', dest='left', type='int',
                  help='position of the feature on the left',
                  metavar='58')
parser.add_option('-r', '--right', dest='right', type='int',
                  help='position of the feature on the right',
                  metavar='1748')
parser.add_option('-w', '--width', dest='width', type='int',
                  help='Camera window width, defaults to 2560.',
                  default=2560,
                  metavar='1920')
parser.add_option('-m', '--magnification', dest='magnification', type='int',
                  help='Magnification',
                  metavar='2')
# read magnification from EPICS!
parser.add_option('-p', '--pixelsize', dest='pixelsize', type='int',
                  help='Pixel size of the camera [um], defaults to 6.5',
                  metavar='6.5',
                  default=6.5)
(options, args) = parser.parse_args()

# Show the help if necessary parameters are missing
if options.left is None or options.right is None or options.magnification is None:
    parser.print_help()
    print 'Example:'
    print 'The command below shows calculates the pos where you have to move'
    print ''
    print sys.argv[0], '-e e11126 -s R108C60'
    print ''
    sys.exit(1)

# Go!
print 80 * '_'

MissedBy = ((options.left + options.right) / 2 - options.width / 2)
print 'You missed the center by', MissedBy, 'pixels'
MoveTo = MissedBy * (options.pixelsize / options.magnification)
print 'You should move the axis', MoveTo, 'um'

print 80 * '_'
