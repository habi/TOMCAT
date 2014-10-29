#!/usr/bin/python

'''
Script to reconstruct a sample with different Paganin parameters.
Very loosely based on Peter Modreggers 'pags' bash script

Use
---
rm /work/sls/bin/PaganinIterator.py
cp ~/Dev/TOMCAT-beamline-scripts/postscan/PaganinIterator.py /work/sls/bin/
chmod 0777 /work/sls/bin/PaganinIterator.py
---
on SLSLc to move it to /work/sls/bin to make it available for all users.
Or do it continuously for testing
---
watch -n 3 "rm /work/sls/bin/PaganinIterator.py;cp
    ~/Dev/TOMCAT-beamline-scripts/postscan/PaganinIterator.py
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
# 2014-01-10: Refactoring
# 2014-01-16: Adapting it to the 'new pipeline' using the SUN grid engine
# 2014-08-06: Making 'waitjobname' (implemented by Kevin) default option

import sys
import os
from optparse import OptionParser
import subprocess
import shutil
import platform
import time
import distutils.util
import logging


# Enable bold and colorful output on the command line (http://is.gd/HCaDv9)
def bold(msg):
    return u'\033[1m%s\033[0m' % msg


def color(string):
    # in the original link, the color is configurable as:
    # return "\033[" + this_color + "m" + string + "\033[0m"
    # but we just use purple
    return "\033[35m" + string + "\033[0m"

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
Parser.add_option('-m', '--Magnitude', dest='Magnitude', default=3, type='int',
                  help='Orders of magnitude you want to iterate through. By '
                       'default the script iterates through %default orders '
                       'of magnitude of *only* delta. If you also want to '
                       'iterate through beta, you need to add the -i '
                       'parameter.',
                  metavar='2')
Parser.add_option('-i', '--IterateBeta', dest='IterateBeta',
                  default=False, action='store_true',
                  help='Iterate over beta. Default: %default',
                  metavar=1)
Parser.add_option('-c', '--Rotationcenter', dest='RotationCenter',
                  type='float',
                  help='RotationCenter for reconstructing the slices. '
                       'Default: Read from logfile or - if not found there - '
                       'half of the x-width of the camera ROI.',
                  metavar='1283.25')
Parser.add_option('-s', '--Slice', dest='Slice', type='int',
                  help='Slice to reconstruct. Default: Middle of camera ROI. '
                       'If you want to reconstruct the full dataset (actually '
                       'every 50th slice), enter 0.',
                  metavar='123')
Parser.add_option('-a', '--Slicesaround', dest='SlicesAround', type='int',
                  default=10,
                  help='Slice to reconstruct around the chosen one (-s). '
                       'Default: %default',
                  metavar='14')
Parser.add_option('--NumProj', dest='NumProj', type='int',
                  help='Number of projections. Default: read from Logfile')
Parser.add_option('--NumDarks', dest='NumDarks', type='int',
                  help='Number of darks. Default: read from Logfile')
Parser.add_option('--NumFlats', dest='NumFlats', type='int',
                  help='Number of flats. Default: read from Logfile')
Parser.add_option('-e', '--Energy', dest='Energy', type='float',
                  help='Beam energy [kV]. Default: read from Logfile')
Parser.add_option('-x', '--Magnification', dest='Magnification', type='float',
                  help='Magnification. Default: read from Logfile')
Parser.add_option('-p', '--Pixelsize', dest='Pixelsize', type='float',
                  help='Actual pixel size [um]. Default: read from Logfile')
Parser.add_option('-v', '--Verbose', dest='Verbose',
                  default=False, action='store_true',
                  help='Be really chatty. Default: %default',
                  metavar=1)
Parser.add_option('-t', '--Test', dest='Test',
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
                        '-d 3e-7 -m 3 -b 3e-10 -z 32')
    print
    sys.exit('Please retry!')
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
    sys.exit('Please retry!')

# Check for mandatory parameters
if options.Delta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Delta value in it.'
    print
    sys.exit('Please enter a Delta value with the -d parameter.')
if options.Beta is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Beta value in it.'
    print
    sys.exit('Please enter a Beta value with the -b parameter.')
if options.Distance is None:
    print 'Your command was "' + ' '.join(sys.argv) + '"'
    print 'I cannot find a Sample-Detector distance in it.'
    print
    sys.exit('Please enter a distance with the -z parameter.')

# Get the sample name from the folder
SampleName = os.path.basename(options.SampleFolder)

# Read Values from LogFile. Ignore them if the user supplied them from the
# commandline
# Define full ROI of pco.Edge as default
X_ROI = [1, 2560]
Y_ROI = [1, 2160]
LogFileLocation = os.path.join(options.SampleFolder, 'tif',
                               SampleName + '.log')
LogFile = open(LogFileLocation, 'r')
# Go through all the lines in the logfile
for line in LogFile:
    # Only do this for existing lines
    if len(line.split()) > 0:
        # Rotation center
        if (line.split()[0] == 'Rotation' and
            line.split()[1] == 'center:'):
            if not options.RotationCenter:
                options.RotationCenter = float(line.split(':')[1])
        # Scan parameters
        elif (line.split()[0] == 'Number' and
               line.split()[2] == 'projections'):
            if not options.NumProj:
                options.NumProj = int(line.split(':')[1])
        elif (line.split()[0] == 'Number' and line.split()[2] == 'darks'):
            if not options.NumDarks:
                options.NumDarks = int(line.split(':')[1])
        elif (line.split()[0] == 'Number' and line.split()[2] == 'flats'):
            if not options.NumFlats:
                options.NumFlats = int(line.split(':')[1])
        # Beam Energy
        elif (line.split()[0] == 'Beam' and line.split()[1] == 'energy'):
            if not options.Energy:
                options.Energy = float(line.split(':')[1])
        # Magnification and pixel size
        elif (line.split()[0] == 'Magnification'):
            if not options.Magnification:
                options.Magnification = float(line.split(':')[1])
        elif (line.split()[0] == 'Actual' and line.split()[1] == 'pixel'):
            if not options.Pixelsize:
                options.Pixelsize = float(line.split(':')[1])
        # Camera ROI
        elif 'ROI' in line.split()[0]:
            if line.split('-')[0] == 'X':
                X_ROI[0] = int(line.split(':')[1].split('-')[0])
                X_ROI[1] = int(line.split(':')[1].split('-')[1])
            elif line.split('-')[0] == 'Y':
                Y_ROI[0] = int(line.split(':')[1].split('-')[0])
                Y_ROI[1] = int(line.split(':')[1].split('-')[1])

# If we cannot find a rotation center in the logfile, save it to be half the
# X_ROI
if not options.RotationCenter:
    options.RotationCenter = X_ROI[1] / 2

# Constructing list of deltas and betas so we can iterate through them below
Delta = ['%.3e' % (options.Delta * 10 ** i) for i in range(-options.Magnitude,
                                                options.Magnitude + 1)]

# If the user wants to iterate through beta, make a list, otherwise just make a
# one-element list
if options.IterateBeta:
    Beta = ['%.3e' % (options.Beta * 10 ** i)
            for i in range(-options.Magnitude, options.Magnitude + 1)]
else:
    Beta = []
    Beta.append('%.3e' % options.Beta)

# Certain parameters are valid for everything, thus we write them into a string
# we can reuse.
DefaultParameters = []
# We always want to create missing directories along the way
DefaultParameters.append('--createMissing')
# We want to have DMPs, so we don't have to think about gray values
DefaultParameters.append('--tifConversionType=0')

# If the user wants to reconstruct the full set, he/she set options.Slice to 0,
# we then reconstruct every 50th sinogram. By default, we reconstruct some
# slices around the middle of the ROI.
if options.Slice == 0:  # evaluates to True if options.Slice is set to 0
    DefaultParameters.append('--steplines=50')
elif not options.Slice:
    options.Slice = sum(Y_ROI) / len(Y_ROI)

# Check if the default or selected slice actually makes sense, i.e is not in
# the first or last ten slices of the ROI. If it is, suggest to reconstruct
# another slice. In the end, set the ROI for reconstruction to be
#'options.SlicesAround' slices around the chosen slice.
if options.Slice - 10 < Y_ROI[0] and not options.Slice == 0:
    sys.exit(' '.join(['Your desired slice is in the first ten slices of', \
        'the dataset, please choose at least', str(Y_ROI[0] + 10), \
        'with the -s option.']))
elif options.Slice + 10 > Y_ROI[1]:
    sys.exit(' '.join(['Your desired slice is not in the last ten slices', \
        'of the dataset, please choose at least', str(Y_ROI[1] - 10), \
        'with the -s option.']))
elif not options.Slice == 0:
    # ROI in projection. Left, right, upper, lower. It's not absolute numbers
    # but lines "cut" from the start and end :)
    DefaultParameters.append('--roiParameters=0,0,' + \
        str(options.Slice - Y_ROI[0] - options.SlicesAround - 1) + ',' + \
        str(Y_ROI[1] - options.Slice - options.SlicesAround))
    if options.Verbose:
        print 'To reconstruct', options.SlicesAround, \
            'slices around slice', options.Slice, 'we cut the ROI'
        print '    * from', \
            options.Slice - Y_ROI[0] - options.SlicesAround - 1, \
            'from the start of the dataset at', Y_ROI[0]
        print '    * to',  Y_ROI[1] - options.Slice - options.SlicesAround,\
            'from the end of it at ' + str(Y_ROI[1]) + '.'
    print

# Inform user what the script is going to do and give him a change to
# renegotiate
print 'Your command-line parameters (' + ' '.join(sys.argv) + \
    ') overwrite the parameters found in the logfile (' + \
    os.path.basename(LogFileLocation) + ').'
print 'The combination of both tells us that the sample', SampleName
print '    * was scanned with', options.NumProj, 'projections,', \
    options.NumDarks, 'darks and', options.NumFlats, 'flats'
print '    * at a beam energy of', options.Energy, 'kV'
print '    * at a', options.Magnification, 'x magnification, resulting in', \
    'a pixel size of', options.Pixelsize, 'um'
print '    * the camera was set to a ROI of x=' + str(X_ROI[0]) + '-' + \
    str(X_ROI[1]), 'and y=' + str(Y_ROI[0]) + '-' + str(Y_ROI[1])
print '    * and the rotation center is', '%0.2f' % options.RotationCenter
print
print 'I will'
if options.Slice:
    print '    * reconstruct', str(options.SlicesAround), \
        'slices above and below slice', options.Slice, '(roi=0,0,' + \
            str(options.Slice - Y_ROI[0] - options.SlicesAround - 1) + ',' + \
            str(Y_ROI[1] - options.Slice - options.SlicesAround) + ')'
else:
    print '    * reconstruct the full dataset'
print '    * with delta(s) of',
for d in Delta:
    print str(d) + ',',
print
print '    * with beta(s) of',
for b in Beta:
    print str(b) + ',',
print
print '    * at a sample-detector distance of', options.Distance, 'mm'
print '    * resulting in', len(Delta) * len(Beta),\
    'different reconstructions'
# Ask the user if everything is correct, otherwise restart the selection
answer = raw_input('---> Is this correct? [Y/n]:')
# See if answer is Enter (not answer) yes or no (strtobool)
if not answer or distutils.util.strtobool(answer):
    print bold("\nHey ho, let's go: http://youtu.be/c1BOsShTyng")
    print 80 * '-'
else:
    print 'Look at the help (' + sys.argv[0], '-h) and overwrite the', \
        'desired parameter with a commandline flag'
    print
    sys.exit('Here It Goes Again: http://youtu.be/dTAAsCNK7RA')

# Save what we do to a logfile
with open(os.path.join(options.SampleFolder, 'PaganinIterator.log'),
                'a') as PaganinLogFile:
    PaganinLogFile.write(10 * '-')
    PaganinLogFile.write(' | PaganinIterator.py command | ')
    PaganinLogFile.write(38 * '-')
    PaganinLogFile.write('\n')
    PaganinLogFile.write(' '.join(sys.argv))
    PaganinLogFile.write('\n')

# At first we need to calculate the corrected projections, since we're gonna
# use them for everything.
cprcommand = ['/afs/psi.ch/project/TOMCAT_pipeline/Beamline/tomcat_pipeline/bin/prj2sinSGE.sh']
# Since the DefaultParameters is already a list, we don't append, but extend
cprcommand.extend(DefaultParameters)
# Give it a nice job name
JobNameCpr = 'cpr_' + SampleName + str(options.Slice)
cprcommand.append('--jobname=' + JobNameCpr)
# Only calculate the corrections
cprcommand.append('--correctionOnly')
# Don't make sinograms
cprcommand.append('--correctionType=3')
# Calulate corrections from TIF images
cprcommand.append('--inputType=1')
# Give the output images a nice prefix
cprcommand.append('--prefix=' + SampleName + '####.tif')
# Numbers of projections, darks, flats, interflats and flat frequency
cprcommand.append('--scanparameters=' + str(options.NumProj) + ',' + \
    str(options.NumDarks) + ',' + str(options.NumFlats) + ',0,0')
# Save it to a nicely named folder, depending if the user want the full set or
# not
if options.Slice:
    cprcommand.append('-o ' + os.path.join(options.SampleFolder,
                                           'cpr_' +
                                           str(options.Slice).zfill(4)))
else:
    cprcommand.append('-o ' + os.path.join(options.SampleFolder, 'cpr'))
# Do it with all these files
cprcommand.append(os.path.join(options.SampleFolder, 'tif'))

if options.Verbose:
    print 'Submitting the calculation of the corrected projections to the', \
    'SGE queue with:'
    print bold(' '.join(cprcommand))
if not options.Test:
    calculatecpr = subprocess.Popen(cprcommand, stdout=subprocess.PIPE)
    output, error = calculatecpr.communicate()
    print 'Corrected projections submitted with Job name', JobNameCpr
    # Write command to logfile
    with open(os.path.join(options.SampleFolder, 'PaganinIterator.log'),
                'a') as PaganinLogFile:
        PaganinLogFile.write('---| ')
        PaganinLogFile.write(time.strftime("%Y.%m.%d@%H:%M:%S",
                                           time.localtime()))
        PaganinLogFile.write(' | Calculating corrected projections, Job name ')
        PaganinLogFile.write(str(JobNameCpr))
        PaganinLogFile.write(' |---\n')
        PaganinLogFile.write(' '.join(cprcommand))
        PaganinLogFile.write('\n')

# Wait a bit, to give everything enough time...
sleepytime = 0.5
time.sleep(sleepytime)

# Calculate filtered projections and reconstructions for each delta and beta
# by submitting it to the SGE queue with the correct commands, waiting for each
# other
print 80 * '-'
if options.Verbose:
    print 'Submitting the calculation of the filtered projections and', \
        'reconstructions for each of the combinations of delta and beta to', \
        'the SGE queue.'
Steps = len(Delta) * len(Beta)
Counter = 0
for d in Delta:
    for b in Beta:
        Counter += 1
        # Generate the output directories. Even though the pipeline supports
        # generating the missing directories, submitting large numbers of jobs
        # didn't work. The hack to make it work is thus to generate all the
        # output directories before submitting the fltp and rec jobs.
        fltpdir = os.path.join(options.SampleFolder, 'fltp_' +
                               str(options.Slice).zfill(4) + '_' + str(d) +
                               '_' + str(b) + '_' + str(options.Distance))
        if not os.path.exists(fltpdir):
            os.makedirs(fltpdir)
        recdir = os.path.join(options.SampleFolder, 'rec_DMP_' +
                              str(options.Slice).zfill(4) + '_' + str(d) +
                              '_' + str(b) + '_' + str(options.Distance))
        if not os.path.exists(recdir):
            os.makedirs(recdir)
        # Inform the user what we'll do
        print color(' '.join([10 * '-', '|', str(Counter) + '/' + str(Steps),
            '| delta', d, '| beta', b, '|', 26 * '-']))
        fltpcommand = ['/afs/psi.ch/project/TOMCAT_pipeline/Beamline/tomcat_pipeline/bin/prj2sinSGE.sh']
        # Add default parameters
        fltpcommand.extend(DefaultParameters)
        # Give it a nice job name
        JobNameFltp = 'fltp_' + SampleName + '_' + str(options.Slice) + '_' + \
	    str(Counter) + '_' + str(d) + '_' + str(b) + '_' + \
            str(options.Distance)
        fltpcommand.append('--jobname=' + JobNameFltp)
        # calculated from DMPs, which are corrected, named so-so
        fltpcommand.append('--inputType=0')
        fltpcommand.append('--correctionOnly')
        fltpcommand.append('--correctionType=0')
        fltpcommand.append('--prefix=' + SampleName + '####.cpr.DMP')
        # Corrected projections don't have darks and flats anymore, only
        # the original number of projections, corrected.
        fltpcommand.append('--scanparameters=' +
                                     str(options.NumProj) + ',0,0,0,0')
        # give it the selected Paganin parameters
        fltpcommand.append('--paganinFilterParams=' +
                                     str(options.Energy) + ',' +
                                     str(options.Pixelsize / 1e6) + ',' +
                                     str(d) + ',' + str(b) + ',' +
                                     str(options.Distance / 1e3))
        # wait for the corrected projections to be done first
        if options.Test:
            fltpcommand.append('--hold=TESTING')
        else:
            fltpcommand.append('--hold=' + JobNameCpr)
        if options.Slice:
            # Save the files here
            fltpcommand.append('-o ' +
                               os.path.join(options.SampleFolder, 'fltp_' +
                                            str(options.Slice).zfill(4) +
                                            '_' + str(d) + '_' + str(b) +
                                            '_' + str(options.Distance)))
            # Do it with those files
            fltpcommand.append(os.path.join(options.SampleFolder, 'cpr_' +
                                        str(options.Slice).zfill(4)))
        else:
            # Save the files here
            fltpcommand.append('-o ' +
                               os.path.join(options.SampleFolder, 'fltp_' +
                                            str(d) + '_' + str(b) + '_' +
                                            str(options.Distance)))
            # Do it with those files
            fltpcommand.append(os.path.join(options.SampleFolder, 'cpr'))
        if options.Verbose:
            print 'Submitting the calculation of the filtered projections', \
                'to the SGE queue with:'
            print bold(' '.join(fltpcommand))
        if not options.Test:
            fltp = subprocess.Popen(fltpcommand, stdout=subprocess.PIPE)
            output, error = fltp.communicate()
            print 'Filtered projections submitted with Job name', JobNameFltp
            # Write command to logfile
            with open(os.path.join(options.SampleFolder,
                                    'PaganinIterator.log'),
                       'a') as PaganinLogFile:
                PaganinLogFile.write('----| ')
                PaganinLogFile.write(time.strftime("%Y.%m.%d@%H:%M:%S",
                                                   time.localtime()))
                PaganinLogFile.write(' | Calculating filtered projections, ')
                PaganinLogFile.write('Job name ')
                PaganinLogFile.write(str(JobNameFltp))
                PaganinLogFile.write(' |---\n')
                PaganinLogFile.write(' '.join(fltpcommand))
                PaganinLogFile.write('\n')

        # Sleep a bit, so that the user has a feeling of stuff happening :)
        time.sleep(sleepytime)

        reconstructioncommand = ['/afs/psi.ch/project/TOMCAT_pipeline/Beamline/tomcat_pipeline/bin/prj2sinSGE.sh']
        # Extending list with DefaultParameters, appending the rest
        reconstructioncommand.extend(DefaultParameters)
        # Use the center of rotation found above or input by the user
        reconstructioncommand.append('--centerOfRotation=' +
                                     str(options.RotationCenter))
        # Use parzen filter and minimal zero padding
        reconstructioncommand.append('--filter=parzen')
        reconstructioncommand.append('--zeroPadding=0.25')
        # Give it a nice job name
        JobNameRecon = 'rec_' + SampleName + '_' + str(options.Slice) + '_' + \
            str(Counter) + '_' + str(d) + '_' + str(b) + '_' + \
            str(options.Distance)
        reconstructioncommand.append('--jobname=' + JobNameRecon)
        # calculated from DMPs, which are corrected, named so-so
        reconstructioncommand.append('--inputType=0')
        reconstructioncommand.append('--correctionType=0')
        reconstructioncommand.append('--prefix=' + SampleName +
                                     '####.fltp.DMP')
        # Corrected projections don't have darks and flats anymore, only
        # the original number of projections, corrected.
        reconstructioncommand.append('--scanparameters=' +
                                     str(options.NumProj) + ',0,0,0,0')
        # Reconstruct with this suffix
        reconstructioncommand.append('--reconstruct=' +
                                     str(options.Slice).zfill(4) + '_' +
                                     str(d) + '_' + str(b) + '_' +
                                     str(options.Distance))
        # wait for the filtered projections to be done first
        if options.Test:
            reconstructioncommand.append('--hold=TESTING')
        else:
            reconstructioncommand.append('--hold=' + JobNameFltp)
        # We don't save the sinograms, but SGE still needs an output directory
        # to save an estimates.txt. Use the rec folder for this
        if options.Slice:
            # Save the files here
            reconstructioncommand.append('-o ' +
                               os.path.join(options.SampleFolder, 'rec_DMP_' +
                                            str(options.Slice).zfill(4) +
                                            '_' + str(d) + '_' + str(b) +
                                            '_' + str(options.Distance)))
            # Do it with those files
            reconstructioncommand.append(os.path.join(
                options.SampleFolder, 'fltp_' + str(options.Slice).zfill(4) +
                '_' + str(d) + '_' + str(b) + '_' + str(options.Distance)))
        else:
            # Save the files here
            reconstructioncommand.append('-o ' +
                               os.path.join(options.SampleFolder, 'rec_DMP_' +
                                            str(d) + '_' + str(b) + '_' +
                                            str(options.Distance)))
            # Do it with those files
            reconstructioncommand.append(os.path.join(options.SampleFolder,
                                                      'fltp_' + str(d) + '_' +
                                                      str(b) + '_' +
                                                      str(options.Distance)))
        if options.Verbose:
            print 'Submitting the calculation of the reconstructions to', \
                'the SGE queue with:'
            print bold(' '.join(reconstructioncommand))
        if not options.Test:
            recs = subprocess.Popen(reconstructioncommand,
                stdout=subprocess.PIPE)
            output, error = recs.communicate()
            print 'Reconstructions submitted with Job name', JobNameRecon
            # Write command to logfile
            with open(os.path.join(options.SampleFolder,
                                    'PaganinIterator.log'),
                       'a') as PaganinLogFile:
                PaganinLogFile.write('------| ')
                PaganinLogFile.write(time.strftime("%Y.%m.%d@%H:%M:%S",
                                                   time.localtime()))
                PaganinLogFile.write(' | Calculating reconstructions, ')
                PaganinLogFile.write('Job name ')
                PaganinLogFile.write(str(JobNameRecon))
                PaganinLogFile.write(' |------\n')
                PaganinLogFile.write(' '.join(reconstructioncommand))
                PaganinLogFile.write('\n')
        # Sleep a bit, so that the user thinks we're working hard :)
        time.sleep(sleepytime)
print 10 * '-', 'done submitting', 53 * '-'

if options.Test:
    print
    print 10 * ' ', 'I was only testing'
    print
    print 'Remove the "-t" flag from your command to actually perform what', \
        'you have asked for.'
    if "cons-2" not in platform.node():
        print 'If you are not running the script on "x02da-cons-2", the', \
            'testing flag is set automatically, since none of the scripts', \
            '(sinooff_tomcat_paganin.py and gridrec) are present on other', \
            ' machines. You thus cannot remove it :)'
    sys.exit('Please retry!')
else:
    print 'Once the SGE queue is done, you will have the following folders', \
        'in', options.SampleFolder + ':'
    print '    * a directory "' + \
        os.path.basename(os.path.join(options.SampleFolder, 'logs')) + \
        '" with commands, logs and errors from the SGE queue'
    if options.Slice:
        print '    * a directory "' + \
            os.path.basename(os.path.join(options.SampleFolder, 'cpr_' +
                             str(options.Slice).zfill(4))) + '"',
    else:
        print '    * a directory "' + \
            os.path.basename(os.path.join(options.SampleFolder, 'cpr')) + \
            '"',
    print 'containing the corrected projections'
    print '    * these directories with filtered projections:'
    for d in Delta:
        for b in Beta:
            if options.Slice:
                print '        *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'fltp_' +
                                                  str(options.Slice).zfill(4) +
                                                  '_' + str(d) + '_' + str(b) +
                                                  '_' + str(options.Distance)))
            else:
                print '        *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'fltp_' + str(d) + '_' +
                                                  str(b) + '_' +
                                                  str(options.Distance)))
    print '    * and these directories with reconstructed DMPs:'
    for d in Delta:
        for b in Beta:
            if options.Slice:
                print '        *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'rec_DMP_' +
                                                  str(options.Slice).zfill(4) +
                                                  '_' + str(d) + '_' + str(b) +
                                                  '_' + str(options.Distance)))
            else:
                print '        *', \
                    os.path.basename(os.path.join(options.SampleFolder,
                                                  'rec_DMP_' + str(d) + '_' +
                                                  str(b) + '_' +
                                                  str(options.Distance)))
    print 80 * '-'

    # Save small bash script to open a set of images images in Fiji
    # Give a meaningful slice if the user selected the full set to reconstruct
    if not options.Slice:
        options.Slice = 1001
    """
    DUE TO THE FACT THAT WE'RE ONLY CALCULATING A ROI, THE SLICES ARE NUMBERED
    "WRONGLY" I.E. THEY ALWAYS START AT 1 AND GO TO 2*(options.SlicesAround +1)
    INSTEAD OF CALLING THE SELECTED SLICE (str(options.Slice).zfill(4)), WE
    THUS OPEN SLICE options.SlicesAround + 1 IN FIJI, WHICH - CONVENIENTLY - IS
    THE MIDDLE ONE :)
    """
    command = 'cd', options.SampleFolder, \
        '\nfor i in `ls rec_*e-* -d`;', \
        '\ndo echo looking at $i;', \
        '\nfiji $i/*' + str(options.SlicesAround + 1) + '* -eval', \
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
        print 'To look at slice', options.Slice, 'of all the reconstructed',  \
            'values, you can use'
        if options.Verbose:
            print '---'
            print command
            print '---'
            print 'or use'
        print color(' '.join(['bash', os.path.join(options.SampleFolder,
                               'PaganinIterator_LookAtReconstruction.sh')]))
        if options.Verbose:
            print 'and close Fiji', str(Steps), 'times, you will then have', \
                'TIF and JPG images to look at.'
    if options.Verbose:
        print 80 * '-'
        print 'Additionally, you have all the commands I executed written', \
            ' to', os.path.join(options.SampleFolder, 'PaganinIterator.log')

print 10 * '-', 'done with all you asked for', 41 * '-'
print 'To look at the SGE queue, use the "qstat" command.'
