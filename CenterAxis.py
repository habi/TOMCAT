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
                  help='position of the feature on the left, at 0 degrees',
                  metavar='58')
parser.add_option('-r', '--right', dest='right', type='int',
                  help='position of the feature on the right, at 180 degrees',
                  metavar='1748')
parser.add_option('-m', '--manual', dest='manual',
                  default=False, action='store_true',
                  help='Do everything manually (if EPICS channels are not '
                  'readable (default=off). If you provide this option, you '
                  'also have to provide the other options (pixel size, window '
                  'width and magnification) manually if you do not like the '
                  'defaults.')
parser.add_option('-p', '--pixelsize', dest='pixelsize', type='float',
                  default=6.5, metavar=11,
                  help='Physical pixel size of the camera. Defaults to 6.5 um '
                  'for the pco.edge. Only needed in manual mode (-m)')
parser.add_option('-w', '--window', dest='windowwidth', type='int',
                  default=2560, metavar=1920,
                  help='Window width of the camera. Defaults to 2560 px, the '
                  'full FOV of the pco.edge. Only needed in manual mode (-m)')
parser.add_option('-x', '--magnification', dest='magnification', type='int',
                  default=10, metavar=4,
                  help='Magnification. Defaults to 10x. Only needed in manual '
                  'mode (-m)')
parser.add_option('-s', '--samplestageposition', dest='samplestageposition',
                  type='float', default=0, metavar=1234,
                  help='Sample stage position. Defaults to 0. Only needed in '
                  ' manual mode (-m)')
parser.add_option('-t', '--test', dest='test',
                  default=True,
                  action='store_true',
                  help='Only calculate, do not move and zero the stage '
                  'position. This is the default option of the script.')
parser.add_option('-g', '--go', dest='test',
                  action='store_false',
                  help='Move the stage! Obviously will not work in manual '
                  'mode (-m)')
(options, args) = parser.parse_args()

# Show the help if necessary parameters are missing
if options.left is None and options.right is None:
    parser.print_help()
    print
    print 'A default call would be', ' '.join(sys.argv), '-l left -r right'
    sys.exit(1)
if options.left is None or options.right is None:
    print
    print 'You need to specify both the left and right position with the',\
        '"-l" & "-r" parameter.'
    print
    if options.right is None:
        print 'Call', ' '.join(sys.argv), '-r right'
    else:
        print 'Call', ' '.join(sys.argv), '-l left'
    sys.exit(1)


# Define EPICSChannel connection stuff (copied from stacked_scan.py)
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
if options.manual:
    Camera = 4
    ActualPixelSize = options.pixelsize / options.magnification
else:
    try:
        ## Initialize the channels
        EPICS_Camera = EpicsChannel('X02DA-ES1-CAM1:CAM_SEL')
        EPICS_PixelSize = EpicsChannel('X02DA-ES1-CAM1:PIXL_SIZE')
        EPICS_NbrOfPixels = EpicsChannel('X02DA-ES1-CAM1:PIX_NBR_H')
        EPICS_Magnification = EpicsChannel('X02DA-ES1-MS:MAGNF')
        EPICS_ActualPixelSize = EpicsChannel('X02DA-ES1-CAM1:ACT_PIXL_SIZE')
        EPICS_Sample_Stage_X = EpicsChannel('X02DA-ES1-SMP1:TRX.VAL')
        EPICS_ZeroPositionToggle = EpicsChannel('X02DA-ES1-SMP1:TRX-SET0.PROC')
        ## Get them values
        Camera = int(EpicsChannel.getVal(EPICS_Camera))
        options.pixelsize = EpicsChannel.getVal(EPICS_PixelSize)
        options.windowwidth = int(EpicsChannel.getVal(EPICS_NbrOfPixels))
        options.magnification = int(EpicsChannel.getVal(EPICS_Magnification))
        ActualPixelSize = EpicsChannel.getVal(EPICS_ActualPixelSize)
        options.samplestageposition = EpicsChannel.getVal(EPICS_Sample_Stage_X)
    except:
        print
        print 'I was not able to read the EPICS channels, you need to fix',\
            ' that first...'
        sys.exit()

# Give the camera ID a nice name
if options.manual:
    CameraName = 'manual settings'
else:
    CameraName = ['pco.2000', 'pco.Dimax', 'pco.edge', 'Photon Science',
                  'manual settings'][Camera]

# Go!
print 80 * '_'
print 'I am calculating with'
print '    - a left (0°) position of', options.left, 'px [-l]'
print '    - a right (180°) position of', options.right, 'px [-r]'
print '    - the', CameraName, 'with a window width of', options.windowwidth,\
    'px'
print '    - a camera pixel size of', options.pixelsize, 'um and'
print '    - a', str(options.magnification) + '-fold magnification,',\
    'resulting in an actual pixel size of', round(ActualPixelSize, 3), 'um.'
print
if options.manual:
    print 'If the default values for pixelsize, magnification and window',\
        'width are not to your liking, please provide them with the "-p",',\
        '"-x" and "-w" parameters to the command line call.'
else:
    print 'If those values are not correct, then make sure the correct',\
        'values are entered'
    print 'in the "Camera Parameter" window (In the Expert Menu under End',\
        'Station 1).'

print 80 * '_'

MissedBy = ((options.left + options.right) / 2 - options.windowwidth / 2)
MoveBy = MissedBy * ActualPixelSize
print 'You missed the center by', abs(round(MissedBy, 3)), 'pixels or',\
    abs(round(MoveBy, 3)), 'um'
print
NewPosition = options.samplestageposition + MoveBy
if options.test:
    print 'I would now move the sample stage from', \
        options.samplestageposition, 'um to', round(NewPosition, 3), 'um'
    if options.manual:
        print 'But I was running in manual mode, so please do it yourself!'
    else:
        print
        print 'To move and center the stage, you have to use the following',\
            'command (i.e. add the "-g" flag to the call of the script)'
        print '---'
        print ' '.join(sys.argv), '-g'
        print '---'
else:
    if options.manual:
        print 'I cannot move in manual mode'
    else:
        print 'I will now move the sample stage from',\
            options.samplestageposition, 'um to', round(NewPosition, 3), 'um'
        #~ EpicsChannel.putval(NewPosition, EPICS_Sample_Stage_X)
        print 'I will now set this position as the new zero position.'
        print 'Not implemented yet, since we need to know how to toggle the',\
            'zero position.'
        # probably EpicsChannel.putval(1,EPICS_ZeroPositionToggle)
        # NOT IMPLEMENTED YET,  WE NEED TO FIND OUT HOW TO TOGGLE IT
        # use "camon X02DA-ES1-SMP1:TRX-SET0.PROC" to see how it's chaning during
        # toggle
print 80 * '_'
