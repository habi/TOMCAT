#!/usr/bin/python

'''
Script to reconstruct a sample with different Paganin parameters.
Very loosely based on Peter Modreggers 'pags' bash script

Use
rm /work/sls/bin/PaganinIterator.py 
cp /afs/psi.ch/user/h/haberthuer/Dev/PaganinIterator.py /work/sls/bin/
chmod 0777 /work/sls/bin/PaganinIterator.py
to make it available for all users. You can probably only use this on SLSLC..
'''

# First version: 2013-02-18: Based on ReconstructSinogram.py
# 2013-02-21: Cleanup
# 2013-02-22: Jacky suggested to add the 'z'-Parameter to the output
# 2013-02-25: Bernd suggested to add a check if commands are run successfully

import sys
import os
import time
from optparse import OptionParser

# clear the commandline
os.system('clear')

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-D', '--Directory', dest='SampleFolder',
                  help='Location of the Sample you want to reconstruct with different parameters differently',
                  metavar='path')
parser.add_option('-d', '--Delta', dest='Delta',
                  type='float',
                  help='Delta you want to start with',
                  metavar='3e-10')
parser.add_option('-b', '--Beta', dest='Beta', type='float',
                  help='Beta you want to start with',
                  metavar='3e-10')
parser.add_option('-z', dest='Distance', default=50, type='int',
                  help='Distance to the scintillator in mm (default = 50mm)',
                  metavar=33)
parser.add_option('-r', '--range', dest='Range', type='int',
                  help='Range of powers you want to iterate through',
                  metavar='3')
parser.add_option('-c', '--center', dest='RotationCenter', type='float',
                  help='RotationCenter for reconstructing the slices (Default=Read from logfile or set to 1024 if nothing found in logfile)',
                  metavar='1280.5')
parser.add_option('-v', '--verbose', dest='Verbose', default=0, action='store_true',
                  help='Be really chatty, (Default of the script is silent)',
                  metavar=1)
parser.add_option('-t', '--test', dest='Test', default=0, action='store_true',
                  help='Only do a test-run to see the details, do not actually reconstruct the slices)',
                  metavar=1)
(options, args) = parser.parse_args()

# show the help if no parameters are given
if options.SampleFolder is None:
    parser.print_help()
    print 'Example:'
    print 'The command below calculates the Paganin reconstuctions of Sample A with Delta values varying from =3e-4 to 3e-10'
    print ''
    print sys.argv[0], '-D /sls/X02DA/data/e12740/Data10/disk1/Sample_A_ -d 3e-7 -r 3 -b 3e-10'
    print ''
    sys.exit(1)

if options.Delta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Delta value.'
    print
    print 'please enter a Delta value with the -d parameter'
    sys.exit(1)

if options.Beta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Beta value.'
    print
    print 'please enter a Beta value with the -b parameter'
    sys.exit(1)

if options.Range is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a range to iterate.'
    print
    print 'please enter a range you want to iterate over with the -r parameter'
    sys.exit(1)

# Assemble Directory- and Samplenames and prepare all other parameters
SampleName = os.path.basename(os.path.abspath(options.SampleFolder))

# Get RotationCenter from Logfile, or set it to 1024 if not found.
if options.RotationCenter is None:
    LogFileLocation = os.path.join(options.SampleFolder, 'tif', SampleName + '.log')
    if options.Verbose:
        print 'Trying to get RotationCenter from', LogFileLocation
    LogFile = open(LogFileLocation, 'r')
    # Go through all the lines in the logfile
    for line in LogFile:
        # split each line at the spaces
        currentline = line.split()
        # if there's a line and the first and second word are "Rotation" and "center"
        # get the value after the :, strip it from all spaces and convert string to number
        # set this value to be the Rotationcenter
        if len(currentline) > 0:
            if (currentline[0] == 'Rotation' and currentline[1] == 'center'):
                options.RotationCenter = float(line.split(':')[1].strip())
    if options.Verbose:
        print 'Rotation center set to', options.RotationCenter
    if options.RotationCenter is None:
        options.RotationCenter = 1024
        if options.Verbose:
            print 'No Rotation center found in LogFile, setting it to 1024.'

if options.Test:
    print 'I would do this if you remove the "-t" flag:'

for i in range(-options.Range, options.Range+1):
    Delta = float(str('%e' % options.Delta)[:-2] + str(int(str('%e' % options.Delta)[-2:]) + i))
    # Construct Paganin-call
    SinogramCommand = ' '.join(['sinooff_tomcat_paganin.py', os.path.abspath(os.path.join(options.SampleFolder, 'tif')), str(Delta), str(options.Beta), str(options.Distance)])
    try:
        os.mkdir(os.path.abspath(os.path.join(options.SampleFolder, 'rec_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance))))
    except:
        pass
    ReconstructionCommand = 'gridrec -f parzen -c ' + str(options.RotationCenter) + ' -D ' + os.path.abspath(os.path.join(options.SampleFolder, 'sin')) + ' -O ' + os.path.abspath(os.path.join(options.SampleFolder, 'rec_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance)))
    MoveSinogramsCommand = ' '.join(['mv', os.path.abspath(os.path.join(options.SampleFolder, 'sin')), os.path.abspath(os.path.join(options.SampleFolder, 'sin_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance)))])
    MoveFilteredProjectionsCommand = ' '.join(['mv', os.path.abspath(os.path.join(options.SampleFolder, 'fltp')), os.path.abspath(os.path.join(options.SampleFolder, 'fltp_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance)))])
    if options.Test:
        print 3 * ' ', SinogramCommand
        print 3 * ' ', ReconstructionCommand
        print 3 * ' ', MoveSinogramsCommand
        print 3 * ' ', MoveFilteredProjectionsCommand
        print 80 * '_'
    else:
        print 'Generating sinograms'
        if os.system(SinogramCommand) is not 0:
            print 'Could not generate sinograms, exiting'
            sys.exit(1)
        print 'Reconstructing sinograms into renamed folder'
        if os.system(ReconstructionCommand)  is not 0:
            print 'Could not reconstruct sinograms, exiting'
            sys.exit(1)
        print 'Renaming sinogram folder'
        if os.system(MoveSinogramsCommand)  is not 0:
            print 'Could not rename sinogram folder, exiting'
            sys.exit(1)
        print 'Renaming filtered projections folder'
        if os.system(MoveFilteredProjectionsCommand) is not 0:
            print 'Could not rename filtered projections folder, exiting'
            sys.exit(1)

if options.Test:
    print 'I was just testing'
else:
    print 'You now have the sinogram directories'
    for i in range(-options.Range, options.Range+1):
        Delta = float(str('%e' % options.Delta)[:-2] + str(int(str('%e' % options.Delta)[-2:]) + i))
        print '    *', os.path.abspath(os.path.join(options.SampleFolder, 'sin_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance)))
    print 'the filtered projection directories'
    for i in range(-options.Range, options.Range+1):
        Delta = float(str('%e' % options.Delta)[:-2] + str(int(str('%e' % options.Delta)[-2:]) + i))
        print '    *', os.path.abspath(os.path.join(options.SampleFolder, 'fltp_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance)))
    print 'and the reconstruction directories'
    for i in range(-options.Range, options.Range+1):
        Delta = float(str('%e' % options.Delta)[:-2] + str(int(str('%e' % options.Delta)[-2:]) + i))
        print '    *', os.path.abspath(os.path.join(options.SampleFolder, 'rec_' + str(Delta) + '_' + str(options.Beta) + '_' + str(options.Distance)))
