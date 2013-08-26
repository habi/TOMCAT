#!/usr/bin/python

'''
Script to calculate the center for the rotation axis.
Should evolve in an automated centering script.
'''

# Import necessary modules
import sys
from optparse import OptionParser
try:
    from CaChannel import *
except:
    print 'I was not able to import the CaChannel module which we need for',\
        'EPICS connection. Exiting.'
    sys.exit(1)
from CaChannel import CaChannelException

# Setup the different options to run the script
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
parser.add_option('-p', '--pixelsize', dest='pixelsize', type='float',
                  help='Pixel size of the camera [um], defaults to 6.5',
                  metavar='6.5',
                  default=6.5)
(options, args) = parser.parse_args()

# Show the help if necessary parameters are missing
if (options.left is None or options.right is None or
    options.magnification is None):
    parser.print_help()
    print 'Example:'
    print 'The command below calculates the position to where you have to',\
        'move the stage if you are using the full width pco.edge (' +\
        str(options.width), 'px) at a 10-fold magnification.'
    print ''
    print sys.argv[0], '-l 123 -r 456 -m 10'
    print ''
    if options.left is None or options.right is None:
        print 10 * ' ' + 40 * '_'
        print 'You need to specify the left and right position with the "-l"',\
            ' & "-r" parameter.'
        print 'Call', ' '.join(sys.argv), '-l left -r right'
        print 10 * ' ' + 40 * '_'
    if options.magnification is None:
        print 10 * ' ' + 40 * '_'
        print 'You need to specify the magnification with the "-m" parameter.'
        print 'Call', ' '.join(sys.argv), '-m Magnification'
        print 10 * ' ' + 40 * '_'
    sys.exit(1)


# Define EPICSChannel connection stuff
class EpicsChannel:
    def __init__(self, pvName):
        self.pvName = pvName
        try:
            self.chan = CaChannel()
            self.chan.search(self.pvName)
            self.chan.pend_io()
            self.connected = 1
        except CaChannelException, status:
            print ca.message(status)
            self.connected = 0

    def getVal(self):
        try:
                val = self.chan.getw()
        except:
                self.connected = 0
                val = ""
        return val

    def getValCHK(self, connected):
        if connected == 1:
            return self.getVal()
        else:
            self.reconnect()

    def putVal(self, val):
        try:
            self.chan.putw(val)
        except:
            self.connected = 0

    def putValCHK(self, val, connected):
        if connected == 1:
            self.putVal(val)
        else:
            self.reconnect()

    def reconnect(self):
        try:
            self.chan = CaChannel()
            self.chan.search(self.pvName)
            self.chan.pend_io()
            self.connected = 1
        except CaChannelException, status:
            print ca.message(status)
            self.connected = 0

# Define relevant EPICS channels
EPICS_Stage = EpicsChannel("X02DA-SCAN-CAM1:FILPRE")

# Go!
print 80 * '_'
print 'I am calculating with'
print '    - a left position of', options.left, 'px [-l]'
print '    - a right position of', options.right, 'px [-r]'
print '    - a camera width of', options.width, 'px [-w]'
print '    - a camera pixel size of', options.pixelsize, 'um [-p] and'
print '    - a', options.magnification, 'fold magnification [-m].'

MissedBy = ((options.left + options.right) / 2 - options.width / 2)
print 'You missed the center by', MissedBy, 'pixels'
MoveTo = MissedBy * (options.pixelsize / options.magnification)
print 'You should move the stage center by', MoveTo, 'um'

print 80 * '_'
