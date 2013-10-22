#!/usr/bin/python

'''
Script to reconstruct a sample with different Paganin parameters.
Very loosely based on Peter Modreggers 'pags' bash script

Use
rm /work/sls/bin/PaganinIterator.py
cp /afs/psi.ch/user/h/haberthuer/Dev/Dev/PaganinIterator.py /work/sls/bin/
chmod 0777 /work/sls/bin/PaganinIterator.py
on SLSLc to move it to /work/sls/bin to make it available for all users.
'''

# First version: 2013-02-18: Based on ReconstructSinogram.py
# 2013-02-21: Cleanup
# 2013-02-22: Jacky suggested to add the 'z'-Parameter to the output
# 2013-02-25: Bernd suggested to add a check if commands are run successfully
# 2013-10-08: Made script less chatty (in general), more informative where
#             necessary and cleaned it up in general.
# 2013-10-14: Iteration is now possible over delta and beta or only delta.

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
                  help='Folder of the Sample you want to reconstruct with the '
                       'different parameters',
                  metavar='path')
parser.add_option('-d', '--Delta', dest='Delta',
                  type='float',
                  help='Delta you want to start with',
                  metavar='3e-10')
parser.add_option('-b', '--Beta', dest='Beta', type='float',
                  help='Beta you want to start with',
                  metavar='3e-10')
parser.add_option('-z', dest='Distance', type='int',
                  help='Distance to the scintillator in mm',
                  metavar=33)
parser.add_option('-r', '--range', dest='Range', type='int',
                  help='Orders of magnitude you want to iterate through. By '
                       'default the script only iterates through delta. If '
                       'you also want to iterate through beta, then add the '
                       '-i parameter.',
                  metavar='3')
parser.add_option('-i', '--iteratebeta', dest='IterateBeta',
                  default=False, action='store_true',
                  help='Iterate over beta. Default: Do not iterate over beta',
                  metavar=1)
parser.add_option('-c', '--center', dest='RotationCenter', type='float',
                  help='RotationCenter for reconstructing the slices. '
                       'Default: Read value from logfile, or set to 1280 if '
                       'if nothing found in logfile.',
                  metavar='1283.25')
parser.add_option('-v', '--verbose', dest='Verbose',
                  default=False, action='store_true',
                  help='Be really chatty. Default: Tell us only the relevant '
                       'stuff.',
                  metavar=1)
parser.add_option('-t', '--test', dest='Test',
                  default=False, action='store_true',
                  help='Only do a test-run to see the details, do not'
                       'actually reconstruct the slices. Default: go for it!',
                  metavar=1)
(options, args) = parser.parse_args()

# show the help if no parameters are given
if options.SampleFolder is None:
    parser.print_help()
    print 'Example:'
    print 'The command below calculates the Paganin reconstuctions of Sample',\
        'A with Delta values varying from 3e-4 to 3e-10, a sample-detector',\
        'distance of 32 mm, while the beta value is kept at 3e-10.'
    print
    print sys.argv[0], ('-D /sls/X02DA/data/e12740/Data10/disk1/Sample_A_ '
                        '-d 3e-7 -r 3 -b 3e-10 -z 32')
    print
    sys.exit(1)

if os.path.exists(os.path.abspath(options.SampleFolder)) is not True:
    print 'I was not able to find', os.path.abspath(options.SampleFolder)
    print ('Please try again with a correct/existing folder. Maybe choose '
           'one of the directories below...')
    os.system('tree -L 1 -d')
    print
    sys.exit(1)

if options.Delta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Delta value in it.'
    print
    print 'Please enter a Delta value with the -d parameter'
    sys.exit(1)

if options.Beta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Beta value in it.'
    print
    print 'Please enter a Beta value with the -b parameter'
    sys.exit(1)

if options.Range is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a range to iterate in it.'
    print
    print 'Please enter a range you want to iterate over with the -r parameter'
    sys.exit(1)

if options.Distance is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Sample-Detector distance in it.'
    print
    print 'Please enter a distance with the -z parameter'
    sys.exit(1)

# Assemble Directory- and Samplenames and prepare all other parameters
SampleName = os.path.basename(os.path.abspath(options.SampleFolder))

# Get RotationCenter from Logfile, or set it to 1280 if not found.
if options.RotationCenter is None:
    LogFileLocation = os.path.join(options.SampleFolder, 'tif',
                                   SampleName + '.log')
    if options.Verbose:
        print 'Getting RotationCenter from', LogFileLocation
    LogFile = open(LogFileLocation, 'r')
    # Go through all the lines in the logfile
    for line in LogFile:
        # split each line at the spaces
        currentline = line.split()
        '''
        If there's a line and the first and second word are "Rotation" and
        "center", then get the value after the :, strip it from all spaces and
        convert string to number. Set this value to be the Rotationcenter
        '''
        if len(currentline) > 0:
            if (currentline[0] == 'Rotation' and currentline[1] == 'center'):
                options.RotationCenter = float(line.split(':')[1].strip())
    print LogFileLocation, 'tells us that the rotation center is',\
        options.RotationCenter
    if options.RotationCenter is None:
        options.RotationCenter = 1280
        if options.Verbose:
            print 'No Rotation center found in LogFile, setting it to', \
                  options.RotationCenter

# Constructing list of deltas and betas so we can iterate through them below
Delta = [options.Delta * 10 ** i for i in range(-options.Range,
                                                options.Range+1)]
# If the user wants to iterate through beta, make a list, otherwise just make a
# one-element list
if options.IterateBeta:
    Beta = [options.Beta * 10 ** i for i in range(-options.Range,
                                                  options.Range+1)]
else:
    Beta = []
    Beta.append(options.Beta)

Counter = 0
for i in range(len(Delta)):
    for k in range(len(Beta)):
        Counter += 1
        print
        print 'Step', str(Counter) + ': Retrieving phase for delta =',\
            str(Delta[i]) + ', beta =', Beta[k], 'and sample-detector',\
            'distance =', options.Distance, 'mm'
        # Construct Paganin-call
        SinogramCommand = ' '.join(['sinooff_tomcat_paganin.py',
                                    os.path.abspath(
                                        os.path.join(options.SampleFolder,
                                                     'tif')),
                                    str(Delta[i]),
                                    str(Beta[k]),
                                    str(options.Distance)])
        if not options.Verbose:
            SinogramCommand = SinogramCommand + ' > /dev/null'
        ReconstructionCommand = 'gridrec -Z 0.5 -f parzen -c ' + \
                                str(options.RotationCenter) + \
                                ' -D ' + \
                                os.path.abspath(os.path.join(
                                    options.SampleFolder, 'sin')) + \
                                ' -O ' + \
                                os.path.abspath(os.path.join(
                                                options.SampleFolder, 'rec_' +
                                                str(Delta[i]) + '_' +
                                                str(Beta[k]) + '_' +
                                                str(options.Distance)))
        if not options.Verbose:
            ReconstructionCommand = ReconstructionCommand + ' > /dev/null'
        MoveSINCommand = ' '.join(['mv',
                                   os.path.abspath(os.path.join(
                                                   options.SampleFolder,
                                                   'sin')),
                                   os.path.abspath(os.path.join(
                                                   options.SampleFolder,
                                                   'sin_' +
                                                   str(Delta[i]) + '_' +
                                                   str(Beta[k]) + '_' +
                                                   str(options.Distance)))])
        MoveFLTPCommand = ' '.join(['mv',
                                    os.path.abspath(os.path.join(
                                                    options.SampleFolder,
                                                    'fltp')),
                                    os.path.abspath(os.path.join(
                                                    options.SampleFolder,
                                                    'fltp_' +
                                                    str(Delta[i]) + '_' +
                                                    str(Beta[k]) + '_' +
                                                    str(options.Distance)))])
        if options.Test:
            print 'with the following sequence of commands:'
            print 3 * ' ', SinogramCommand
            print 3 * ' ', 'mkdir',\
                os.path.abspath(os.path.join(options.SampleFolder, 'rec_' +
                                             str(Delta[i]) + '_' +
                                             str(Beta[k]) + '_' +
                                             str(options.Distance)))
            print 3 * ' ', ReconstructionCommand
            print 3 * ' ', MoveSINCommand
            print 3 * ' ', MoveFLTPCommand
            print 80 * '_'
        else:
            print 'Generating corrected projections, filtered projections',\
                ' and sinograms'
            print 'This will take quite a while!'
            if options.Verbose:
                print 'Especially if we are doing it for the first run of',\
                    'the iteration process. Afterwards we can reuse the',\
                    'corrected projections.'
            if os.system(SinogramCommand) is not 0:
                print 'Could not generate sinograms, exiting'
                print
                print 'You should try to remove the fltp folder and try again.'
                print 'Use "rm ',\
                    os.path.abspath(os.path.join(options.SampleFolder,
                                    'fltp')), '-r" to delete the stray fltp',\
                    ' directory and try again.'
                print
                print 'If that does *not* work, you can also delete the cpr',\
                    'folder with "; rm ',\
                    os.path.abspath(os.path.join(options.SampleFolder,
                                                 'cpr')),\
                    '-r".'
                print 'Maybe you should cancel some batches in the DicoClient.'
                print '"cd /usr/local/cluster/DiCoClient"'
                print '"java -jar DiCoClient.jar"'
                print '"lj ex a" and "cb number" of the jobs belonging to you'
                sys.exit(1)
            print 'Generating Folder for reconstruction:',\
                os.path.abspath(os.path.join(options.SampleFolder,
                                             'rec_' + str(Delta[i]) + '_' +
                                             str(Beta[k]) + '_' +
                                             str(options.Distance)))
            try:
                os.mkdir(os.path.abspath(os.path.join(options.SampleFolder,
                                                      'rec_' + str(Delta[i]) +
                                                      '_' + str(Beta[k]) +
                                                      '_' +
                                                      str(options.Distance))))
            except:
                pass
            print 'Reconstructing sinograms into folder mentioned above'
            print
            print 25 * ' ' + 'This will take a (long) while!'
            if os.system(ReconstructionCommand) is not 0:
                print 'Could not reconstruct sinograms, exiting'
                sys.exit(1)
            print 'Renaming old sinogram folder'
            if os.system(MoveSINCommand) is not 0:
                print 'Could not rename sinogram folder, exiting'
                sys.exit(1)
            print 'Renaming old filtered projections folder'
            if os.system(MoveFLTPCommand) is not 0:
                print 'Could not rename filtered projections folder, exiting'
                sys.exit(1)

if options.Test:
    print
    print 31 * ' ', 'I was only testing'
    print
    print 'Remove the "-t" flag from your command to actually perform what',\
        'you have asked for.'
    print
else:
    print 'You now have the sinogram directories'
    for i in range(len(Delta)):
        for k in range(len(Beta)):
            print '    *', os.path.abspath(os.path.join(options.SampleFolder,
                                                        'sin_' +
                                                        str(Delta[i]) + '_' +
                                                        str(Beta[k]) + '_' +
                                                        str(options.Distance)))
    print 'the filtered projection directories'
    for i in range(len(Delta)):
        for k in range(len(Beta)):
            print '    *', os.path.abspath(os.path.join(options.SampleFolder,
                                                        'fltp_' +
                                                        str(Delta[i]) + '_' +
                                                        str(Beta[k]) + '_' +
                                                        str(options.Distance)))
    print 'and the reconstruction directories'
    for i in range(len(Delta)):
        for k in range(len(Beta)):
            print '    *', os.path.abspath(os.path.join(options.SampleFolder,
                                                        'rec_' +
                                                        str(Delta[i]) + '_' +
                                                        str(Beta[k]) + '_' +
                                                        str(options.Distance)))
    print
    print 'To look at a single slice of all the reconstructed values, you',\
        'can use the command below.'
    print 'This command opens up reconstruction 1001 from each different',\
        'beta-value directory, enhances the contrast of this image and saves',\
        'it to a tiff- and jpf-file in the current directory. The only thing',\
        'you have to do is to close fiji X times (x=amount of values you',\
        'reconstructed).'
    print '---'
    print 'cd', os.path.abspath(options.SampleFolder)
    print 'for i in `ls rec_*e-* -d`;'
    print 'do echo looking at $i;'
    print 'fiji $i/*1001* -eval "rename(\\\"${i}\\\");',\
        'run(\\\"Enhance Contrast...\\\", \\\"saturated=0.4\\\");',\
        'run(\\\"Save\\\", \\\"save=' +\
        os.path.abspath(options.SampleFolder) + '\/${i}.tif\\\");',\
        'saveAs(\\\"Jpeg\\\", \\\"' +\
        os.path.abspath(options.SampleFolder) + '\/${i}.jpg\\\");";'
    print 'done'
    print '---'
