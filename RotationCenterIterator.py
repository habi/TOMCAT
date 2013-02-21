#!/usr/bin/python

'''
Script to iteratively test rotation centers
Calls 'gridrec_zp_64' on gws-2 with a range on rotation centers
renames the reconstructed slices and calls fiji so one can look at the
differently reconstructed slices in a stack.
'''

# Update: 10.01.2012: Fiji is only started in the end, so we don't
# interrupt the workflow. Additionally, at the start of the script we
# delete all *.rec.DMPs in the sinogram directory. And using 'optparse'
# we provide some options, help and sensible defaults to the user.

# Update 16.4.2012: Now needs to be called with sin-directory, but also
# allows for uncommon naming of those. Additionally test if we have three-
# or four-digit numbers of Sinograms (both by suggestion of Jacky Sun).

# Update 21.5.2012: Now cleanly reads the Sample- and Sin-Dir with os.abspath
# calls. Additionally one can now specify a filter to pass through to
# gridrec, by suggestion from Peter Modregger.

# Update 23.5.2012: Calls gridrec_32 or gridrec_64, depending on architecture.
# Also doesn't call 'gridrec_zp' anymore, since this was an old version.
# Both suggested by Peter M.

# Update 11.6.2012: Now directly opens the reconstructed Sinograms as a stack.
# Since I couldn't figure out how to do it directly, I'm just calling a
# a "macro" at the commandline-call of Fiji to open as Image Sequence.

# Update 11.9.2012: corrected typo in the help, now reliably deletes *.rec.DMPs
# and writes out the sinograms with the necessary amount of trailing zeroes
# so that the slices open correctly in fiji (before they were opened in the
# wrong order if 0.25 was used as interval). Additionally also checks if
# the sinogram in question really does exist.

# Update 8.10.2012: Platform-check is done more pythony, some cosmetic
# corrections and query the user if more than MaxReconstructions
# reconstructions are requested if we should really do it

# Update 5.11.2012: Jacky found out that the (undocumente) parzen filter
# of gridrec is not supported. Now it is. This made Fede document all filters
# in Gridrec.

# Update 19.11.2012: Now reads RotationCenter from Logfile (if the user did
# not specify a value). If no value is found, RotationCenter is set to 1024.

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
parser.add_option('-s', '--sinogram', dest='Sinogram', default=1001, type='int',
                  help='Sinogram Number you want to reconstruct with different rotation center (Default=1001)',
                  metavar='51')
parser.add_option('-c', '--center', dest='RotationCenter', type='float',
                  help='RotationCenter for reconstructing the slices (Default=Read from logfile or set to 1024 if nothing found in logfile)',
                  metavar='2037.5')
parser.add_option('-r', '--range', dest='Range', default=4, type='float',
                  help='Use this as a range to iterate around the RotationCenter (Default=4)',
                  metavar='3')
parser.add_option('-i', '--iteration', dest='Iteration', default=0.5, type='float',
                  help='Use this value as iteration step, (Default=0.5)',
                  metavar=0.5)
parser.add_option('-z', dest='ZeroPadding', default=0.5, type='float',
                  help='ZeroPadding, (Default=0.5)',
                  metavar=0.5)
parser.add_option('-f', '--filter', dest='Filter', type='str',
                  help='Filter to use (passthrough to "gridrec"). Options are obviously the same as for gridrec: shlo or shepp (default), hann, hamm or hamming, ramp or ramlak, none, parz or parzen, lanc or dpc.',
                  metavar='parzen')
parser.add_option('-v', '--verbose', dest='Verbose', default=0, action='store_true',
                  help='Be really chatty, (Default of the script is silent)',
                  metavar=1)
parser.add_option('-d', '--debug', dest='debug', default=0, action='store_true',
                  help='Debug the script. This omits all error-checking and never exits the script',
                  metavar=1)
parser.add_option('-t', '--test', dest='Test', default=0, action='store_true',
                  help='Only do a test-run to see the details, do not actually reconstruct the slices)',
                  metavar=1)
(options, args) = parser.parse_args()

# show the help if no parameters are given
if options.SinDir is None:
    parser.print_help()
    print 'Example:'
    print 'The command below reconstructs the DPC-Sinogram "Sample_A_1001.sin.DMP" with Rotationcenters varying in 0.5-steps from 2013.0 to 2019:'
    print ''
    print sys.argv[0], '-D /sls/X02DA/data/e12740/Data10/disk1/Sample_A_/sin_dpc -s 1001 -c 2016 -r 3 -i 0.5 -f dpc'
    print ''
    sys.exit(1)

def query_yes_no(question, default="yes"):
    # from http://code.activestate.com/recipes/577058/
    '''
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    '''
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
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

# Assemble Directory- and Samplenames and prepare all other parameters
## test if the directory exists, if not, tell the user
if os.path.exists(options.SinDir) is False:
    print
    print 'Directory "' + options.SinDir + '" not found, please try again with full (and correct) path.'
    print
    if options.debug is False:
        sys.exit(1)
try:
    SampleName = os.path.basename(os.path.dirname(os.path.abspath(options.SinDir)))
    # abspath "converts" trailing backslash or not to a nice path, getting
    # rid of relative pathnames. The dirname wrapped around it gets rid
    # of the Sin-Directory and the additional basename around it extracts
    # the Directory-name of the sample.
except:
    print 'I was not able to deduce a SampleName from your input.'
    print "Please specify a path like this './samplename/sin_something' with the '-D'-option."
    print 'It is probably best if you try again with the absolute path...'
    if options.debug is False:
        sys.exit(1)

# Get RotationCenter from Logfile, or set it to 1024 if not found.
if options.RotationCenter is None:
    LogFileLocation = os.path.join(os.path.split(os.path.abspath(options.SinDir))[0], 'tif', SampleName + '.log')
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

# Make a vector with the Rotationcenter varying from Rot-Range to Rot+Range in 'Iteration' steps.
RotationCenter = np.arange(
    options.RotationCenter-options.Range,
    options.RotationCenter+options.Range+options.Iteration,
    options.Iteration)

# If the user is not testing and we would reconstruct more than MaxReconstructions
# Rotationcenters ask for permission to do so, since this will take a while...
MaxReconstructions = 25
if options.Test is False:
    if len(RotationCenter) > MaxReconstructions:
        if query_yes_no('Are you sure that you want to reconstruct ' + str(len(RotationCenter)) + ' different RotationCenters?', default='no') == 'no':
            print 'Quitting'
            print
            print 'Maybe add the "-t" flag to the call to', sys.argv[0], 'to see what would be done'
            sys.exit(1)
        else:
            print 'Ok, you asked for it! Proceeding...'

if options.debug:
    print 'Iteration set to', options.Iteration
    print 'RotationCenter set to', RotationCenter

'''
According to Fede, the filters in gridrec are:
    * Shepp-Logan (default)  (called by shlo or shepp)
    * Hanning (hann)
    * Hamming (hamm or hamming)
    * Ramp (ramp or ramlak)
    * None (none)
    * Parzen (parz or parzen)
    * Lanczos (lanc)
    * Dpc (dpc)
'''

# Test if the user input the correct filter name (if any).
if options.Filter:
    if options.Filter in ('dpc', 'hann', 'hamm', 'hamming', 'lanc', 'parz', 'parzen', 'ramlak', 'ramp', 'shlo', 'shepp', 'none'):
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
    if os.path.exists(options.SinDir + '/' + SampleName + str(Sinogram) + '.sin.DMP') is False:
        Sinogram = "%.03d" % options.Sinogram
except:
    print 'Help! I was not able to find three- or four-digit numbers of sinograms'
    if options.debug is False:
        sys.exit(1)

# See if the Sinogram in question actually exists. If not, exit.
if os.path.exists(os.path.abspath(options.SinDir) + '/' + SampleName + str(Sinogram) + '.sin.DMP') is False:
    print 'Help! The requested sinogram (' + options.SinDir + '/' + SampleName + str(Sinogram) + '.sin.DMP) does not exist.'
    print 'Did you select one of the', len(glob.glob(options.SinDir + '/' + SampleName + '*.sin.DMP')), 'sinograms below?'
    for file in range(len(glob.glob(options.SinDir + '/' + SampleName + '*.sin.DMP'))):
        print np.sort(glob.glob(options.SinDir + '/' + SampleName + '*.sin.DMP')[file])
    print 'Please enter a sinogram-number that actually exists for the Parameter "-s".'
    if options.debug is False:
        sys.exit(1)

# Give out some feedback to the user what we'll do
print ''
print 'I will:'
print '  - reconstruct ' + SampleName + str(Sinogram) + '.sin.DMP'
print '  - with', len(RotationCenter), 'Rotationcenter steps of size', options.Iteration, 'varying around', options.RotationCenter
print '  - varying from', str(RotationCenter[0]) + ',', str(RotationCenter[1]) + ', etc. up to', RotationCenter[-1]

# From prior runs there might be some reconstructed DMPs in the sinogram-
# Folder. Delete these, as it might confuse Fiji/the user when loading
# all files at the end of the script
if len(glob.glob(os.path.abspath(options.SinDir) + '/' + SampleName + str(Sinogram) + '*.rec.DMP')) > 1:
    deletecommand = 'rm ' + options.SinDir + '/' + SampleName + '*.rec.DMP'
    if options.Verbose:
        print 80 * '_'
        print
        print 'Deleting', len(glob.glob(os.path.abspath(options.SinDir) + '/' + SampleName + str(Sinogram) + '*.rec.DMP')), '*.rec.DMP in "' + options.SinDir + ', left from previous runs of this script with the command', deletecommand
    os.system(deletecommand)

# Calculate Sinograms
print 80 * '_'
print
if options.Test:
    print 'I would actually calculate', len(RotationCenter), 'reconstructions here, but I am only testing...'
else:
    for i in range(len(RotationCenter)):
        # Reconstruct with gridrec
        print '|' + (i+1)*'=' + (len(RotationCenter)-(i+1))*'-' + '| ' + "%02d" % (i+1) + '/' + "%02d" % len(RotationCenter) + ', ' + SampleName + str(Sinogram) + '.sin.DMP, ' + str(RotationCenter[i])
        # Call either 64bit or 32bit gridrec
        # platform.architecture[0] gives out either '32bit' or '64bit', with [:-3] we remove the 'bit'
        # afterwards we add the other paramteres to the reccommand
        reccommand = 'gridrec_' + platform.architecture()[0][:-3] + ' -c ' + str(RotationCenter[i]) + ' ' + options.SinDir + '/' + SampleName + str(Sinogram) + '.sin.DMP' + ' -Z ' + str(options.ZeroPadding)
        if options.Filter:
            # Add filter to the end of the command (if the user specified one)
            reccommand += ' -f ' + options.Filter
        if options.Verbose:
            print 'Reconstructing RotationCenter ' + str(RotationCenter[i]) + ' with the command'
            print reccommand
            os.system(reccommand)
        else:
            os.system(reccommand + '> /dev/null')
        # Rename the reconstructed file to 'filename.rotationcenter.rec.dmp'
        renamecommand = 'mv ' + os.path.abspath(options.SinDir) + '/' + SampleName + str(Sinogram) + '.rec.DMP ' + os.path.abspath(options.SinDir) + '/' + SampleName + str(Sinogram) + '.' + str("%.03f" % RotationCenter[i]) + '.rec.DMP'
        if options.Verbose:
            print 80 * '_'
            print
            print 'renaming reconstructed file so we can differentiate between Rotationcenters'
            print renamecommand
        os.system(renamecommand)

# Display Calculated Sinograms for the User
if options.Test is False:
    viewcommand = 'fiji -eval \'run("Image Sequence...", "open=' + os.path.abspath(options.SinDir) + ' starting=1 increment=1 scale=100 file=rec or=[] sort");\' &'
    os.system(viewcommand)
    print 80 * '_'
    print
    print 'Starting Fiji with all the reconstructed files with the command'
    print
    print viewcommand
    print
    print 'Since the files have been renamed, you should be able browse through the'
    print 'stack and thus find the best Rotationcenter!'

print 80 * '_'
print
print 'Done with', len(RotationCenter), 'Rotationcenters:'
print '  - of Sinogram', Sinogram
print '  - of Sample', SampleName
print '  - varying from', str(RotationCenter[0]) + '-' + str(RotationCenter[-1])

print 80 * '_'

if options.Test:
    print
    print '                 I was just testing, nothing really happened!'
    print 80 * '_'
