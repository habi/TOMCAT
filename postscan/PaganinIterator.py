#!/usr/bin/python

'''
Script to reconstruct a sample with different Paganin parameters.
Very loosely based on Peter Modreggers 'pags' bash script

Use
---
rm /work/sls/bin/PaganinIterator.py
cp /afs/psi.ch/user/h/haberthuer/Dev/postscan/PaganinIterator.py /work/sls/bin/
chmod 0777 /work/sls/bin/PaganinIterator.py
---
on SLSLc to move it to /work/sls/bin to make it available for all users.
Or do it continuously for testing
---
watch -n 3 "rm /work/sls/bin/PaganinIterator.py;
cp /afs/psi.ch/user/h/haberthuer/Dev/postscan/PaganinIterator.py
/work/sls/bin/;chmod 0777 /work/sls/bin/PaganinIterator.py"
---
'''

# First version: 2013-02-18: Based on ReconstructSinogram.py
# 2013-02-21: Cleanup
# 2013-02-22: Jacky suggested to add the 'z'-Parameter to the output
# 2013-02-25: Bernd suggested to add a check if commands are run successfully
# 2013-10-08: Made script less chatty (in general), more informative where
#             necessary and cleaned it up in general.
# 2013-10-14: Iteration is now possible over delta and beta or only delta.
# 2014-01-10: Implementing multiprocessor option, analogue to
#             RotationCenterIterator.py

import sys
import os
from optparse import OptionParser
import subprocess
import shutil
import platform
import time

# clear the commandline
os.system('clear')

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
Parser = OptionParser()
Parser.add_option('-D', '--Directory', dest='SampleFolder',
                  help='Folder of the Sample you want to reconstruct with the '
                       'different parameters. Mandatory.',
                  metavar='path')
Parser.add_option('-d', '--Delta', dest='Delta',
                  type='float',
                  help='Delta you want to start with. Mandatory.',
                  metavar='3e-10')
Parser.add_option('-b', '--Beta', dest='Beta', type='float',
                  help='Beta you want to start with. Mandatory.',
                  metavar='3e-10')
Parser.add_option('-z', dest='Distance', type='int',
                  help='Distance to the scintillator in mm. Mandatory.',
                  metavar=33)
Parser.add_option('-r', '--range', dest='Range', default=3, type='int',
                  help='Orders of magnitude you want to iterate through. By '
                       'default the script iterates through %default orders '
                       'of magnitude of *only* delta. If you also want to '
                       'iterate through beta, you need to add the -i '
                       'parameter.',
                  metavar='2')
Parser.add_option('-i', '--iteratebeta', dest='IterateBeta',
                  default=False, action='store_true',
                  help='Iterate over beta. Default: %default',
                  metavar=1)
Parser.add_option('-c', '--center', dest='RotationCenter', type='float',
                  help='RotationCenter for reconstructing the slices. '
                       'Default: Read value from logfile, or set to 1280 if '
                       'if nothing found in logfile.',
                  metavar='1283.25')
Parser.add_option('-s', '--slice', dest='Slice', type='int', default=1001,
                  help='If you do not want to reconstruct the full dataset '
                       'you can select a slice with this parameter. Default: '
                       '%default',
                  metavar='3')
Parser.add_option('-v', '--verbose', dest='Verbose',
                  default=False, action='store_true',
                  help='Be really chatty. Default: %default',
                  metavar=1)
Parser.add_option('-t', '--test', dest='Test',
                  default=False, action='store_true',
                  help='Only do a test-run to see the details, do not '
                       'actually reconstruct the slices. Default: %default',
                  metavar=1)
(options, Arguments) = Parser.parse_args()

# Show the help if no parameters are given, otherwise convert path to sample to
# absolute path
if options.SampleFolder is None:
    Parser.print_help()
    print 'Example:'
    print 'The command below calculates the Paganin reconstuctions of', \
        'Sample A with Delta values varying from 3e-4 to 3e-10, a', \
        'sample-detector distance of 32 mm, while the beta value is kept at', \
        '3e-10.'
    print
    print sys.argv[0], ('-D /sls/X02DA/data/e12740/Data10/disk1/Sample_A_ '
                        '-d 3e-7 -r 3 -b 3e-10 -z 32')
    print
    sys.exit(1)
else:
    options.SampleFolder = os.path.abspath(options.SampleFolder)

# Switch to 'test' mode if we are not on console 2, since the necessary
# commands cannot run.
if "cons-2" not in platform.node():
    print 'We are not running on "x02da-cons-2", switching "test" to "True"', \
        'on, so we can run the script'
    options.Test = True

# See if the desired sample folder actually exist
if not os.path.exists(options.SampleFolder):
    print 'I was not able to find', options.SampleFolder
    print 'Please try again with a correct/existing folder. Maybe choose', \
           'one of the directories below...'
    os.system('tree -L 1 -d')
    print
    sys.exit(1)

# Check for mandatory parameters
if options.Delta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Delta value in it.'
    print
    sys.exit('Please enter a Delta value with the -d parameter')
if options.Beta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Beta value in it.'
    print
    sys.exit('Please enter a Beta value with the -b parameter')
if options.Distance is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Sample-Detector distance in it.'
    print
    sys.exit('Please enter a distance with the -z parameter')

# Assemble Directory- and Samplenames and prepare all other parameters
SampleName = os.path.basename(options.SampleFolder)

# Get RotationCenter from Logfile if the user didn't specify it. If we cannot
# find a value, set to default of 1280, half the width of the pco.Edge.
if options.RotationCenter is None:
    LogFileLocation = os.path.join(options.SampleFolder, 'tif',
                                   SampleName + '.log')
    LogFile = open(LogFileLocation, 'r')
    # Go through all the lines in the logfile
    for line in LogFile:
        # If there's a line and the first and second word are "Rotation" and
        # "center", then get the value after the :, strip it from spaces and
        # set the float of this value to be the Rotationcenter
        if len(line.split()) > 0:
            if (line.split()[0] == 'Rotation' and
                line.split()[1] == 'center:'):
                options.RotationCenter = float(line.split(':')[1].strip())
    if options.Verbose:
        print os.path.basename(LogFileLocation), \
            'tells us that the rotation center is', options.RotationCenter
    if options.RotationCenter is None:
        options.RotationCenter = 1280
        if options.Verbose:
            print 'No Rotation center found in', LogFileLocation
            print 'Setting Rotation center to', options.RotationCenter

# Get camera ROI from Logfile to see if the desired slice actually makes sense,
# i.e is not in the first or last ten slices. If it is, suggest to reconstruct
# another slice
# Set ROI to full field of pco.Edge
X_ROI = [1, 2560]
Y_ROI = [1, 2160]
LogFileLocation = os.path.join(options.SampleFolder, 'tif', SampleName +
                               '.log')
LogFile = open(LogFileLocation, 'r')
# Go through all the lines in the logfile
for line in LogFile:
    # If there's a line and we either see 'X-ROI' or 'Y-ROI' as the first word
    # get the data after the :, split it at '-' and save these values.
    if len(line.split()) > 0:
        if 'ROI' in line.split()[0]:
            if line.split('-')[0] == 'X':
                X_ROI[0] = int(line.split(':')[1].split('-')[0])
                X_ROI[1] = int(line.split(':')[1].split('-')[1])
                found = True
            elif line.split('-')[0] == 'Y':
                Y_ROI[0] = int(line.split(':')[1].split('-')[0])
                Y_ROI[1] = int(line.split(':')[1].split('-')[1])
                found = True
            else:
                pass
if options.Verbose:
    if found:
        print os.path.basename(LogFileLocation), \
            'tells us that the camera X-ROI is',  X_ROI[0], '-', X_ROI[1], \
            'and Y-ROI', Y_ROI[0], '-', Y_ROI[1]
    else:
        print 'Using default settings for ROI (full field of pco.Edge)'
if options.Slice - 10 < Y_ROI[0]:
    sys.exit(' '.join(['Your desired slice is not in the first ten slices', \
        'of the dataset, please choose at least', str(Y_ROI[0] + 10), \
        'with the -s option.']))
if options.Slice + 10 > Y_ROI[1]:
    sys.exit(' '.join(['Your desired slice is not in the last ten slices', \
        'of the dataset, please choose at least', str(Y_ROI[0] - 10), \
        'with the -s option.']))

# Constructing list of deltas and betas so we can iterate through them below
Delta = ['%.3e' % (options.Delta * 10 ** i) for i in range(-options.Range,
                                                options.Range + 1)]

# If the user wants to iterate through beta, make a list, otherwise just make a
# one-element list
if options.IterateBeta:
    Beta = ['%.3e' % (options.Beta * 10 ** i) for i in range(-options.Range,
                                                  options.Range + 1)]
else:
    Beta = []
    Beta.append('%.3e' % options.Beta)


def generatesinograms(Folder, Delta, Beta,
                      DetectorDistance=options.Distance):
    '''
    Generate command to calculate sinograms for a sample "Folder" and the
    given "Delta", "Beta" and "Sample-Detector-Distance". The verbose option of
    the script is carried over as an optional input to this function, according
    to http://is.gd/ChFkUB
    '''
    cmd = ['sinooff_tomcat_paganin.py', os.path.join(Folder, 'tif'), Delta,
           Beta, DetectorDistance]
    # Append the command to a LogFile
    with open(os.path.join(options.SampleFolder, 'PaganinIterator.log'),
               'a') as LogFile:
        LogFile.write(80 * '-')
        LogFile.write('\nDelta=')
        LogFile.write(str(Delta))
        LogFile.write(' | Beta=')
        LogFile.write(str(Beta))
        LogFile.write(' | Sample-detector distance=')
        LogFile.write(str(DetectorDistance))
        LogFile.write('\n=')
        LogFile.write(time.strftime("%Y.%m.%d@%H:%M:%S", time.localtime()))
        LogFile.write(': Calculating Sinograms with\n')
        LogFile.write(str(' '.join(map(str, cmd))))
        LogFile.write('\n')
    # The 'cmd' is mixed between int and str. Map every item to a string,
    # then join all the item with spaces and return this as a string
    return map(str, cmd)


def reconstruct(Folder, Delta, Beta, DetectorDistance=options.Distance,
                RotCenter=options.RotationCenter):
    '''
    Generate command to reconstruct a "Folder" of sinograms with a given
    "Delta", "Beta" "Sample-Detector-Distance" and a "RotationCenter" into a
    folder with a distinctive name. The verbose and Rotationcenter options of
    the script are carried over as optional input to this function.
    '''
    cmd = ['gridrec_' + platform.architecture()[0][:-3], '-Z', '0.25', '-f',
           'parzen', '-c', RotCenter, '-D', os.path.join(Folder, 'sin'),
            '-O', os.path.join(Folder, 'rec_' + str(Delta) + '_' + str(Beta) +
                               '_' + str(DetectorDistance))]
    # Append the command to a LogFile
    with open(os.path.join(options.SampleFolder, 'PaganinIterator.log'),
               'a') as LogFile:
        LogFile.write(time.strftime("%Y.%m.%d@%H:%M:%S", time.localtime()))
        LogFile.write(': Reconstructing sinograms with\n')
        LogFile.write(str(' '.join(map(str, cmd))))
        LogFile.write('\n')
    return map(str, cmd)

Steps = len(Delta) * len(Beta)
Counter = 0
for d in Delta:
    for b in Beta:
        Counter += 1
        print
        print 15 * '-', '|', str(Counter) + '/' + str(Steps),  '| delta', \
            d, '| beta', b, '|', 15 * '-'
        if Counter == 1:
            print 'Generating Sinograms, corrected and filtered projections'
        else:
            print 'Generating Sinograms and filtered projections'
        # The first call of 'sinooff_paganin' generates corrected projections
        # in the 'cpr' folder, this takes a while. All subsequent calls use the
        # corrected projections to calculate the filtered projection in the
        # 'fltp' folder.
        if options.Test:
            if options.Verbose:
                print ' '.join(generatesinograms(options.SampleFolder, d, b))
        else:
            # If the sinogram command does not exit with 0, something wentf
            # b0nkers. Inform the user about what to possibly do.
            try:
                if options.Verbose:
                    subprocess.call(generatesinograms(options.SampleFolder, d,
                                                      b))
                else:
                    with open(os.devnull, 'wb') as devnull:
                        subprocess.call(generatesinograms(options.SampleFolder,
                                                          d, b),
                                        stdout=devnull,
                                        stderr=subprocess.STDOUT)
            except Exception, b0nkers:
                print
                print 'Sinogram generation failed with:', b0nkers
                print
                print 'I removed the "fltp" directory, you you can', \
                    'probably just try again.'
                try:
                    shutil.rmtree(os.path.join(options.SampleFolder, 'fltp'))
                except:
                    'I was not able to remove the "fltp" folder, maybe you', \
                    'need to do it yourself. If that does not work, you can', \
                    'also delete the "cpr" folder and start from scratch.'
                print
                print 'If just retrying does not work, you probably need', \
                    'to remove the corrected projections and cancel batch', \
                    'jobs. Use'
                print '    rm', os.path.join(options.SampleFolder, 'fltp'), \
                    '-r'
                print 'to delete the "fltp" and/or'
                print '    rm', os.path.join(options.SampleFolder, 'cpr'), \
                    '-r'
                print 'to delete the "cpr" folder. Maybe you also need to', \
                    'cancel batch jobs in the DicoClient. Start it with.'
                print '   cd /usr/local/cluster/DiCoClient; java -jar', \
                    'DiCoClient.jar'
                print 'Use "lj ex a" to list all jobs and "cb number" to', \
                    'cancel a certain batch job. With "exit" you get out of', \
                    'the DiCoClient and "cd -" brings you back to the', \
                    'directory you were before this whole shenanigan happened.'
                sys.exit(1)
        if Counter == 1:
            print 'This will take a *long* time, especially for the first', \
                'time'
        print 'Reconstructing Sinograms'
        if options.Test:
            if options.Verbose:
                print ' '.join(reconstruct(options.SampleFolder, d, b))
        else:
            print 'DOES IT ALSO WORK WITHOUT THE mkdir OF THE REC FOLDER?'
            try:
                os.mkdir(os.path.join(options.SampleFolder, 'rec_' + d + '_' +
                                      b + '_' + str(options.Distance)))
            except:
                pass
            try:
                if options.Verbose:
                    subprocess.call(reconstruct(options.SampleFolder, d, b))
                else:
                    with open(os.devnull, 'wb') as devnull:
                        subprocess.call(reconstruct(options.SampleFolder, d,
                                                    b), stdout=devnull,
                                        stderr=subprocess.STDOUT)
            except Exception, b0nkers:
                print
                print 'Reconstruction failed with:', b0nkers
        # Move Sinograms from (automatically generated) 'sin'-folder to a
        # folder with a nice name. This makes it possible to reuse them.
        if options.Verbose:
            print 'Renaming sinograms to sin_' + str(d) + '_' + str(b) + \
                '_' + str(options.Distance)
        if not options.Test:
            try:
                shutil.move(os.path.join(options.SampleFolder, 'sin'),
                            os.path.join(options.SampleFolder, 'sin_' +
                                         str(d) + '_' + str(b) + '_' +
                                         str(options.Distance)))
            except IOError or OSError:
                sys.exit('Could not rename sinogram folder')
        # Move filtered projections to a folder with a nice name.
        if options.Verbose:
            print 'Renaming filtered projections to fltp_' + str(d) + '_' + \
                str(b) + '_' + str(options.Distance)
        if not options.Test:
            try:
                shutil.move(os.path.join(options.SampleFolder, 'fltp'),
                            os.path.join(options.SampleFolder, 'fltp_' +
                                         str(d) + '_' + str(b) + '_' +
                                         str(options.Distance)))
            except IOError or OSError:
                sys.exit('Could not rename folder with reconstructed files')

if options.Test:
    print
    print 31 * ' ', 'I was only testing'
    print
    print 'Remove the "-t" flag from your command to actually perform what', \
        'you have asked for.'
    if "cons-2" not in platform.node():
        print 'If you are not running the script on "x02da-cons-2", the', \
            'testing flag is set automatically, since none of the scripts', \
            '(sinooff_tomcat_paganin.py and gridrec) are present on other', \
            ' machines. You thus cannot remove it :)'
    print
else:
    if options.Verbose:
        print 'In', options.SampleFolder, 'you now have'
        print 'the sinogram directories'
        for d in Delta:
            for b in Beta:
                print '    *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'sin_' + str(d) + '_' +
                                                  str(b) + '_' +
                                                  str(options.Distance)))
        print 'the filtered projection directories'
        for d in Delta:
            for b in Beta:
                print '    *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'fltp_' + str(d) + '_' +
                                                  str(b) + '_' +
                                                  str(options.Distance)))
        print 'and the reconstruction directories'
        for d in Delta:
            for b in Beta:
                print '    *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'rec_' + str(d) + '_' +
                                                  str(b) + '_' +
                                                  str(options.Distance)))

    # Save small bash script to open a set of images images in Fiji
    command = 'cd', options.SampleFolder, \
        '\nfor i in `ls rec_*e-* -d`;', \
        '\ndo echo looking at $i;', \
        '\nfiji $i/*' + str('%04d' % options.Slice) + '* -eval', \
        '"rename(\\\"${i}\\\"); run(\\\"Enhance Contrast...\\\",', \
        '\\\"saturated=0.4\\\"); run(\\\"Save\\\", \\\"save=' + \
        options.SampleFolder + '\/${i}.tif\\\"); saveAs(\\\"Jpeg\\\", \\\"' + \
        options.SampleFolder + '\/${i}.jpg\\\");";', \
        '\ndone'
    command = ' '.join(command)
    with open(os.path.join(options.SampleFolder,
                            'PaganinIterator_LookAtReconstruction.sh'),
               'w') as CommandFile:
        CommandFile.write(command)
    if not options.Test:
        print
        print 'To look at slice', options.Slice, 'of all the reconstructed',  \
            'values, you can use'
        if options.Verbose:
            print '---'
            print command
            print '---'
            print 'or use'
        print 'bash', os.path.join(options.SampleFolder,
                                    'PaganinIterator_LookAtReconstruction.sh')
        if options.Verbose:
            print 'and close Fiji', str(Steps), 'times, you will then have', \
                'TIF and JPG images to look at.'

    print
    print 'Additionally, you have all the commands I executed written to', \
        os.path.join(options.SampleFolder, 'PaganinIterator.log')
