#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReplaceProjections.py | David Haberthür <david.haberthuer@psi.ch>

Script to iteratively test rotation centers.
Calls 'gridrec_zp_64' on gws-2 with a range on rotation centers.
Renames the reconstructed slices and calls fiji so one can look at the
differently reconstructed slices in a stack.
"""

import sys
import os
import glob
import numpy as np
import time
from optparse import OptionParser
import platform

# clear the commandline
os.system('clear')

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-D', '--Directory', dest='SinDir',
                  help='Location of the Sinogramfolder of the Sample you want '
                  'to test different Rotationcenters on',
                  metavar='path')
parser.add_option('-s', '--sinogram', dest='Sinogram',
                  default=1001,
                  type='int',
                  help='Sinogram Number you want to reconstruct with '
                  'different rotation center (Default=1001)',
                  metavar='51')
parser.add_option('-c', '--center', dest='RotationCenter',
                  type='float',
                  help='RotationCenter for reconstructing the slices '
                  '(Default=Read from logfile or set to 1024 if nothing found '
                  'in logfile)',
                  metavar='2037.5')
parser.add_option('-r', '--range', dest='Range',
                  default=4,
                  type='float',
                  help='Use this as a range to iterate around the '
                  'RotationCenter (Default=4)',
                  metavar='3')
parser.add_option('-i', '--iteration', dest='Iteration',
                  default=0.5,
                  type='float',
                  help='Use this value as iteration step, (Default=0.5)',
                  metavar=0.5)
parser.add_option('-z', dest='ZeroPadding',
                  default=0.5,
                  type='float',
                  help='ZeroPadding, (Default=0.5)',
                  metavar=0.5)
parser.add_option('-f', '--filter', dest='Filter',
                  type='str',
                  help='Filter to use (passing through to "gridrec"). Options '
                  'are obviously the same as for gridrec: shlo or shepp '
                  '(default), hann, hamm or hamming, ramp or ramlak, none, '
                  'parz or parzen, lanc or dpc.',
                  metavar='parzen')
parser.add_option('-g', '--geometry', dest='Geometry',
                  type='int',
                  help='Geometry to use (passing through to "gridrec"). '
                  'Options are obviously the same as for gridrec: "0" '
                  '(projections angles specified in a file named angles.txt), '
                  '1 (homogeneous sampling between 0 and pi) and 2 '
                  '(homogeneous sampling between 0 and 2pi). Default: 1',
                  metavar='1')
parser.add_option('-m', '--multicore', dest='Multicore',
                  default=True,
                  action='store_true',
                  help='Use multiple cores. To make this work, you have to '
                  'load additional modules! Use "module load xbl/epd_free" in '
                  'the terminal to try to load those. They should be there '
                  'on "x02da-cons-2".',
                  metavar=1)
parser.add_option('--singlecore', action='store_false', dest='Multicore',
                  help='turns off multicore processing, everything will take '
                  'much longer')
parser.add_option('-v', '--verbose', dest='Verbose',
                  default=False,
                  action='store_true',
                  help='Be really chatty, (Default of the script is silent)',
                  metavar=1)
parser.add_option('-d', '--debug', dest='debug',
                  default=False,
                  action='store_true',
                  help='Debug the script. This omits all error-checking and '
                  'does not exit the script on errors',
                  metavar=1)
parser.add_option('-t', '--test', dest='Test',
                  default=False,
                  action='store_true',
                  help='Only do a test-run to see the details, do not '
                  'actually reconstruct the slices)',
                  metavar=1)
(options, args) = parser.parse_args()

# show the help if no parameters are given
if options.SinDir is None:
    parser.print_help()
    print 'Example:'
    print 'The command below reconstructs the DPC-Sinogram',\
        '"Sample_A_1001.sin.DMP" with Rotationcenters varying in 0.5-steps',\
        'from 2013.0 to 2019:'
    print ''
    print sys.argv[0], '-D /sls/X02DA/data/e12740/Data10/disk1/Sample_A_/' +\
        'sin_dpc -s 1001 -c 2016 -r 3 -i 0.5 -f dpc'
    print ''
    sys.exit(1)


def query_yes_no(question, default="yes"):
    # from http://code.activestate.com/recipes/577058/
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": "yes", "y": "yes", "ye": "yes", "no": "no", "n": "no"}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y'",
                             " or 'n').\n")


def worker(i, rotcenter, options, name, sin):
    """
    Makes all the actual work ;).
    1/ Creates temporary directory,
    2/ Generates slice into tmp directory (gridrec reconstruction)
    3/ Moves-renames the slice from tmp directory
    4/ Deletes tmp directory

    Example of the generated command used for gridrec:
    ---
    gridrec_64 -c 1302.39 -D ./Data10/disk5/PBT180s20xD_3_/sin/
    PBT180s20xD_3_0901.sin.DMP -Z 0.5
    -O /sls/X02DA/data/e13869/Data10/disk5/PBT180s20xD_3_/sin/1302.390/
    ---
    """

    # Reconstruct with gridrec
    print '|' + (i + 1) * '=' + (len(rotcenter) - (i + 1)) * '-' +\
        '| ' + "%02d" % (i + 1) + '/' + "%02d" % len(rotcenter) + ', ' +\
        name + str(sin) + '.sin.DMP, ' + str(rotcenter[i])
    # Call either 64bit or 32bit gridrec
    # platform.architecture[0] gives out '32bit' or '64bit', with [:-3] we
    # remove the 'bit' and afterwards add the other paramteres to the command

    if platform.node()[0:6] == "merlin":
        reccommand = '/afs/psi/project/TOMCAT_pipeline/Merlin/' +\
            'tomcat_pipeline/src/Reconstruction/lib/gridRec -c ' +\
            str(rotcenter[i]) + ' -D ' + options.SinDir + '/ ' +\
            name + str(sin) + '.sin.DMP' + ' -Z ' +\
            str(options.ZeroPadding)
    else:
        reccommand = 'gridrec_' + platform.architecture()[0][:-3] + ' -c ' +\
            str(rotcenter[i]) + ' -D ' + options.SinDir + '/ ' +\
            name + str(sin) + '.sin.DMP' + ' -Z ' +\
            str(options.ZeroPadding)
    if options.Filter:
        # Add filter to the end of the command (if the user specified one)
        reccommand += ' -f ' + options.Filter
    if options.Geometry:
        # Add filter to the end of the command (if the user specified one)
        reccommand += ' -g ' + str(options.Geometry)

    # Create temporary directory for reconstruction of rotation center
    tmp_dir = options.SinDir + '/' + str("%.03f" % rotcenter[i]) + '/'
    if not os.path.exists(tmp_dir):
        if options.Verbose:
            print 'The temporary directory is:', tmp_dir
        os.makedirs(tmp_dir)

    # Set output directory for gridrec
    reccommand += ' -O ' + os.path.abspath(tmp_dir) + '/'

    if options.Verbose:
        print 'Reconstructing RotationCenter ' + str(rotcenter[i]) +\
            ' with the command'
        print reccommand
        os.system(reccommand)
    else:
        os.system(reccommand + '> /dev/null')

    # Rename the reconstructed file to 'filename.rotationcenter.rec.dmp'
    renamecommand = 'mv ' + os.path.abspath(tmp_dir) + '/' + name +\
        str(sin) + '.rec.DMP ' + os.path.abspath(options.SinDir) + '/' +\
        name + str(sin) + '.' + str("%.03f" % rotcenter[i]) +\
        '.rec.DMP'
    if options.Verbose:
        print 80 * '_'
        print
        print 'renaming reconstructed file so we can differentiate between',\
            'Rotationcenters'
        print renamecommand
    os.system(renamecommand)

    # Remove temporary directory
    if options.Verbose:
        print 'Removing temporary directory:', tmp_dir
    os.removedirs(tmp_dir)

# Assemble Directory- and Samplenames and prepare all other parameters
# test if the directory exists, if not, tell the user
if os.path.exists(options.SinDir) is False:
    print
    print 'Directory "' + options.SinDir + '" not found, please try again',\
        'with full (and correct) path.'
    print
    if options.debug is False:
        sys.exit(1)
try:
    # os.path.abspath gets rid of any relative pathnames and outputs the
    # full path. The os.path.dirname gets rid of the Sin-directory and the
    # additional basename around it gives us the directory in which we'll
    # find the sample.
    SampleName = os.path.basename(
        os.path.dirname(os.path.abspath(options.SinDir)))
except:
    print 'I was not able to deduce a SampleName from your input.'
    print "Please specify a path like './samplename/sin_something' with the",\
        "'-D'-option."
    print 'It is probably best if you try again with the absolute path...'
    if options.debug is False:
        sys.exit(1)

# Get RotationCenter from Logfile, or set it to 1024 if not found.
if options.RotationCenter is None:
    LogFileLocation = os.path.join(os.path.dirname(os.path.abspath(
                                                   options.SinDir)),
                                   'tif', SampleName + '.log')
    if options.Verbose:
        print 'Trying to get RotationCenter from', LogFileLocation
    try:
        LogFile = open(LogFileLocation, 'r')
    except:
        print 'I cannot seem to find a log file!'
        print 'You told me to look here:', os.path.abspath(options.SinDir)
        print 'Maybe you only told me about the sample folder and forgot to',\
            'include the sinogram folder. Care to try again?'
        sys.exit(1)
    # Go through all the lines in the logfile
    for line in LogFile:
        # split each line at the spaces
        currentline = line.split()
        """
        If there's a line and the first and second word are "Rotation" and
        "center", then get the value after the :, strip it from all spaces,
        convert the string to a float and set this float to be the
        Rotationcenter.
        """
        if len(currentline) > 0:
            if currentline[0] == 'Rotation' and currentline[1] == 'center':
                options.RotationCenter = float(line.split(':')[1].strip())
    if options.Verbose:
        print 'Rotation center set to', options.RotationCenter
    if options.RotationCenter is None:
        options.RotationCenter = 1024
        if options.Verbose:
            print 'No Rotation center found in LogFile, setting it to 1024.'

# Make a vector with the Rotationcenter varying from Rot-Range to Rot+Range in
# 'Iteration' steps.
RotationCenter = np.arange(
    options.RotationCenter - options.Range,
    options.RotationCenter + options.Range + options.Iteration,
    options.Iteration)

# If the user is not testing and we would reconstruct more than
# 'MaxReconstructions' Rotationcenters ask for permission to do so, since this
# will take a while...
MaxReconstructions = 25
if options.Test is False:
    if len(RotationCenter) > MaxReconstructions:
        if query_yes_no('Are you sure that you want to reconstruct ' +
                        str(len(RotationCenter)) +
                        ' different RotationCenters?', default='no') == 'no':
            print 'Quitting'
            print
            print 'Maybe add the "-t" flag to the call to', sys.argv[0],\
                'to see what would be done'
            sys.exit(1)
        else:
            print 'Ok, you asked for it! Proceeding...'

if options.debug:
    print 'Iteration set to', options.Iteration
    print 'RotationCenter set to', RotationCenter

# Test if the user input the correct filter name (if any).
if options.Filter:
    if options.Filter in ('dpc', 'hann', 'hamm', 'hamming', 'lanc', 'parz',
                          'parzen', 'ramlak', 'ramp', 'shlo', 'shepp', 'none'):
        print 'Passing the "' + options.Filter + '" Filter to gridrec.'
    else:
        print 'You probably have a ypot in the filter-name. :)'
        print 'You can only enter one of these:'
        print '    * Shepp-Logan (default)  (called by shlo or shepp)'
        print '    * Hanning (hann)'
        print '    * Hamming (hamm or hamming)'
        print '    * Ramp (ramp or ramlak)'
        print '    * None (none)'
        print '    * Parzen (parz or parzen)'
        print '    * Lanczos (lanc)'
        print '    * Dpc (dpc)'
        print 'Please try again!'
        if options.debug is False:
            sys.exit(1)

# Decide if 100s or 1000s of Sinograms
try:
    Sinogram = "%.04d" % options.Sinogram
    if os.path.exists(options.SinDir + '/' + SampleName + str(Sinogram) +
                      '.sin.DMP') is False:
        Sinogram = "%.03d" % options.Sinogram
except:
    print 'Help! I was not able to find either three- or four-digit numbers',\
        'of sinograms'
    if options.debug is False:
        sys.exit(1)

# See if the Sinogram in question actually exists. If not, exit.
if os.path.exists(os.path.abspath(options.SinDir) + '/' + SampleName +
                  str(Sinogram) + '.sin.DMP') is False:
    print 'Help! The requested sinogram (' + options.SinDir + '/' +\
        SampleName + str(Sinogram) + '.sin.DMP) does not exist.'
    print 'Did you select one of the',\
        len(glob.glob(options.SinDir + '/' + SampleName + '*.sin.DMP')),\
        'sinograms below?'
    for sinogram in range(len(glob.glob(options.SinDir + '/' + SampleName +
                                        '*.sin.DMP'))):
        print np.sort(glob.glob(options.SinDir + '/' + SampleName +
                                '*.sin.DMP')[sinogram])
    print 'Please enter a sinogram-number that actually exists for the',\
        'Parameter "-s".'
    if options.debug is False:
        sys.exit(1)

# Give out some feedback to the user what we'll do
print ''
print 'I will:'
print '  - reconstruct ' + SampleName + str(Sinogram) + '.sin.DMP'
print '  - with', len(RotationCenter), 'Rotationcenter steps of size',\
    options.Iteration, 'varying around', options.RotationCenter
print '  - varying from', str(RotationCenter[0]) + ',',\
    str(RotationCenter[1]) + ', etc. up to', RotationCenter[-1]

# From prior runs there might be some reconstructed DMPs in the sinogram-
# folder. Delete these, as it might confuse Fiji/the user when loading all
# files at the end of the script
if len(glob.glob(os.path.abspath(options.SinDir) + '/*rec*')) > 1:
    deletecommand = 'rm ' + options.SinDir + '/' + SampleName + '*.rec.DMP'
    if options.Verbose:
        print 80 * '_'
        print
        print 'Deleting',\
            len(glob.glob(os.path.abspath(options.SinDir) + '/*rec*')),\
            '*.rec.DMP in "' + options.SinDir +\
            ', left from previous runs of this script with the command',\
            deletecommand
    os.system(deletecommand)

# Calculate Sinograms
print 80 * '_'
print
if options.Test:
    print 'I would actually calculate', len(RotationCenter),\
        'reconstructions here, but I am only testing...'
else:
    if options.Multicore:
        try:
            import multiprocessing
        except:
            print 'I can not import the python module multiprocessing.'
            print 'Additional modules have to be loaded! Run'
            print '---'
            print 'module load xbl/epd_free'
            print '---'
            print 'to try to load them. Afterwards (if you are on x02da-cn*)'
            print 'you unfortunately need to call the script with the absolute'
            print 'path and "python" before it. Try with'
            print '---'
            print 'python', ' '.join(sys.argv)
            print '---'
            sys.exit(1)
        print 'Splitting the sinogram calculation over',\
            multiprocessing.cpu_count(), 'cores.'
        print
        if options.Verbose:
            print
            print 'Logging will be messy, since we are using',\
                multiprocessing.cpu_count(), 'independent processes.'
            time.sleep(5)
        pool = multiprocessing.Pool()

        for i in range(len(RotationCenter)):
            pool.apply_async(worker, (i, RotationCenter, options, SampleName,
                                      Sinogram))

        pool.close()
        pool.join()
    else:
        print 'Using a single core to calculate the sinograms'
        for i in range(len(RotationCenter)):
            worker(i, RotationCenter, options, SampleName, Sinogram)

# Display Calculated Sinograms for the User
if options.Test:
    print
    output = 'I was just testing, nothing really happened!'
    # make sure the test string is in the middle of a 80 chars long line :)
    print (int(round(80 / 2 - (len(output) + 3) / 2)) + 1) * ' ' + output
    print
    print 80 * '_'
else:
    if platform.node()[0:6] == "merlin":
        viewcommand = '/opt/fiji/Fiji.app/fiji-linux64 -eval ' +\
            '\'run("Image Sequence...", "open=' +\
            os.path.abspath(options.SinDir) +\
            ' starting=1 increment=1 scale=100 file=rec or=[] sort");\' &'
    else:
        viewcommand = 'fiji -eval \'run("Image Sequence...", "open=' +\
            os.path.abspath(options.SinDir) +\
            ' starting=1 increment=1 scale=100 file=rec or=[] sort");\' &'
    os.system(viewcommand)
    print 80 * '_'
    print
    print 'Starting Fiji with all the reconstructed files with the command'
    print
    print '\033[1m' + viewcommand + '\033[0;0m'
    print
    print 'Since the files have been renamed, you should be able browse',\
        'through the stack and thus find the best Rotationcenter!'

    print 80 * '_'
    print
    print 'Done with', len(RotationCenter), 'Rotationcenters:'
    print '  - of Sinogram', Sinogram
    print '  - of Sample', SampleName
    print '  - varying from', str(RotationCenter[0]) + '-' +\
        str(RotationCenter[-1])
    print 80 * '_'
