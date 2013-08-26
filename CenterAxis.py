#!/usr/bin/python
# -*- coding: utf-8 -*-

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
usage = 'usage: %prog [options] arg'
parser.add_option('-l', '--left', dest='left', type='int',
                  help='position of the feature on the left, at 0',
                  metavar='58')
parser.add_option('-r', '--right', dest='right', type='int',
                  help='position of the feature on the right, at 180',
                  metavar='1748')
parser.add_option('-t', '--test', dest='test',
                  default=True,
                  action='store_true',
                  help='Only testing (default, since we are otherwise moving '
                  'the sample stage).')
parser.add_option('-g', '--go', dest='test',
                  action='store_false',
                  help='Move the stage!')

(options, args) = parser.parse_args()

# Show the help if necessary parameters are missing
if options.left is None or options.right is None:
    parser.print_help()
    print 'You need to specify the left and right position with the "-l"',\
        ' & "-r" parameter.'
    print 'Call', ' '.join(sys.argv), '-l left -r right'
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
                val = ''
        return val

    def putVal(self, val):
        try:
            self.chan.putw(val)
        except:
            self.connected = 0

# Define relevant EPICS channels
## Initialize the channels
EPICS_Sample_Stage_X = EpicsChannel('X02DA-ES1-SMP1:TRX.VAL')
EPICS_PixelSize = EpicsChannel('X02DA-ES1-CAM1:PIXL_SIZE')
EPICS_NbrOfPixels = EpicsChannel('X02DA-ES1-CAM1:PIX_NBR_H')
EPICS_Magnification = EpicsChannel('X02DA-ES1-MS:MAGNF')
EPICS_ActualPixelSize = EpicsChannel('X02DA-ES1-CAM1:ACT_PIXL_SIZE')
EPICS_ZeroPositionToggle = EpicsChannel('X02DA-ES1-SMP1:TRX-SET0.PROC')
## Get them values
PixelSize = EpicsChannel.getVal(EPICS_PixelSize)
WindowWidth = int(EpicsChannel.getVal(EPICS_NbrOfPixels))
Magnification = int(EpicsChannel.getVal(EPICS_Magnification))
ActualPixelSize = EpicsChannel.getVal(EPICS_ActualPixelSize)
SampleStagePosition = EpicsChannel.getVal(EPICS_Sample_Stage_X)

# Go!
print 80 * '_'
print 'I am calculating with'
print '    - a left (0°) position of', options.left, 'px [-l]'
print '    - a right (180°) position of', options.right, 'px [-r]'
print '    - a camera width of', WindowWidth, 'px'
print '    - a camera pixel size of', PixelSize, 'um and'
print '    - a', str(Magnification) + '-fold magnification.'
print
print 'If those values are not correct, then make sure the correct values',\
    'are entered'
print 'in the "Camera Parameter" window (In the Expert Menu under End',\
    'Station 1).'

print 80 * '_'

MissedBy = ((options.left + options.right) / 2 - WindowWidth / 2)
MoveBy = MissedBy * (PixelSize / Magnification)
print 'You missed the center by', abs(MissedBy), 'pixels or', abs(MoveBy), 'um'
print
NewPosition = SampleStagePosition + MoveBy
if options.test:
    print 'I would now move the sample stage from', SampleStagePosition, 'um'\
        'to', NewPosition, 'um'
else:
    print 'I will now move the sample stage from', SampleStagePosition, 'um'\
        'to', NewPosition, 'um'
    #~ EpicsChannel.putval(NewPosition, EPICS_Sample_Stage_X)
    print 'I will now set this position as the new zero position.'
    print 'Not implemented yet, since we need to know how to toggle the zero',\
        'position'
    # EpicsChannel.putval(EPICS_ZeroPositionToggle)
    # NOT IMPLEMENTED YET,  WE NEED TO FIND OUT HOW TO TOGGLE IT
    # use "camon X02DA-ES1-SMP1:TRX-SET0.PROC" to see how it's chaning during
    # toggle
print 80 * '_'
