#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ReplaceProjections.py | David Haberthür <david.haberthuer@psi.ch>

Script to replace darks, flats or projections of one sample with the darks,
flats or projections of another sample. Made after an user group of David once
had set the 'out-of-beam'-position too small, so that the sample was still
visible in the flat images.
"""

import sys
import os
from optparse import OptionParser

def query_yes_no(question, default="yes"):
    # from http://code.activestate.com/recipes/577058/
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":"yes", "y":"yes", "ye":"yes", "no":"no", "n":"no"}
    if default == None:
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

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-i', '--insample', dest='insample',
    help='Sample to load the darks, flats or projectons from',
    metavar='Sample1')
parser.add_option('-o', '--outsample', dest='outsample',
    help='Sample to load the darks, flats or projectons from',
    metavar='Sample1')
parser.add_option('-d', '--darks', dest='darks', default=0, action='store_true',
    help='Copy the Darks',
    metavar=1)
parser.add_option('-f', '--flats', dest='flats', default=0, action='store_true',
    help='Copy the Flats',
    metavar=1)
parser.add_option('-p', '--proj', dest='projections', default=0, action='store_true',
    help='Copy the Projections',
    metavar=1)
parser.add_option('-v', '--verbose', dest='verbose', default=0, action='store_true',
    help='Be really chatty, (Default is off, so the script is quite silent)',
    metavar=1)
parser.add_option('-t', '--test', dest='Test', default=0, action='store_true',
	help='Only do a test-run to see the details, do not actually reconstruct the slices)',
	metavar=1)
(options, args) = parser.parse_args()

# show the help if no parameters are given
if options.insample==None:
	parser.print_help()
	print 'Example:'
	print 'The command below copies the darks and flats from "Sample_A_" to "Sample_B_"'
	print ''
	print 'ReplaceProjections.py --insample=Data10/disk3/Sample_A_ --outsample=Data10/disk3/Sample_B_ --darks --flats'
	print 'or'
	print 'ReplaceProjections.py -i Sample_A_ -o Sample_B_ -d -f'
	print ''
	sys.exit(1)

if options.insample and options.outsample==None:
	print 'You specified an input, but no output-sample.'
	sys.exit(1)

# Assemble Directory- and Samplenames
## test if the directory exists, if not, tell the user
if os.path.exists(os.path.abspath(options.insample)) == False:
	print '---'
	print 'Input-Directory "' + options.insample + '" not found, please try again with correct path.'
	print '---'
	sys.exit(1)
try:
	InputPath = os.path.abspath(options.insample)
	InputSample = os.path.basename(InputPath)
except:
	print 'I was not able to deduce an Input-Sample from your command.'
	print "Please specify a path like this './samplename/' with the '-i'-option."
	
if os.path.exists(os.path.abspath(options.outsample)) == False:
	print '---'
	print 'Output-Directory "' + options.outsample + '" not found, please try again with correct path.'
	print '---'
	sys.exit(1)
try:
	OutputPath = os.path.abspath(options.outsample)
	OutputSample = os.path.basename(OutputPath)
except:
	print 'I was not able to deduce an Output-Sample from your command.'
	print "Please specify a path like this './samplename/' with the '-o'-option."
	
# Read Number of Darks, Flats and Projections from Logfile of *Output*-sample
LogFile2Location = os.path.join(OutputPath,'tif',OutputSample + '.log')
LogFile2 = open(LogFile2Location,'r')
for line in LogFile2:
	linelist=line.split()
	if len(linelist)>0:
   	   if (linelist[0]=="Number" and linelist[2]=="projections"):
			Projections = int(linelist[4])
   	   elif (linelist[0]=="Number" and linelist[2]=="darks"):
     		Darks = int(linelist[4])
   	   elif (linelist[0]=="Number" and linelist[2]=="flats"):
      		Flats = int(linelist[4])
LogFile2.close()

print 'The logfile tells us that'
print 'For sample',OutputSample,'we recorded',Darks,'darks,',Flats,'flats and',Projections,'projections.'

# Compare those with the *Input*-values and abort if not the same (and abort is desired)
LogFile1Location = os.path.join(InputPath,'tif',InputSample + '.log')
LogFile1 = open(LogFile1Location,'r')
for line in LogFile1:
	linelist=line.split()
	if len(linelist)>0:
   	   if (linelist[0]=="Number" and linelist[2]=="projections"):
			Projections1 = int(linelist[4])
   	   elif (linelist[0]=="Number" and linelist[2]=="darks"):
     		Darks1 = int(linelist[4])
   	   elif (linelist[0]=="Number" and linelist[2]=="flats"):
      		Flats1 = int(linelist[4])
LogFile1.close()
print 'For sample',InputSample,'we recorded',Darks1,'darks,',Flats1,'flats and',Projections1,'projections.'

if options.darks==None and options.flats==None and options.projections==None:
	print
	print 'You need to tell me what to do!'
	print "Either specify the '-d' option to copy the darks or "
	print "or specify the '-f' option to copy the flats or "
	print "or specify the '-p' option to copy the projections. (Or multiple options...)"
	sys.exit()

if options.darks:
	if Darks != Darks1:
		print 'Number of darks for',InputSample,'(' + str(Darks1) + ') and',OutputSample,'(' + str(Darks) + ') do not match'
		if query_yes_no('Really copy the darks, even though their number do not match?',default='no')=='no':
			print 'Quitting'
			sys.exit(1)
if options.flats:
	if Flats != Flats1:
		print 'Number of flats for',InputSample,'(' + str(Flats1) + ') and',OutputSample,'(' + str(Flats) + ') do not match'
		if query_yes_no('Really copy the flats, even though their number do not match?',default='no')=='no':
			print 'Quitting'
			sys.exit(1)
if options.projections:
	if Projections != Projections1:
		print 'Number of projections for',InputSample,'(' + str(Projections1) + ') and',OutputSample,'(' + str(Projections) + ') do not match'
		if query_yes_no('Really copy the projections, even though their number do not match?',default='no')=='no':
			print 'Quitting'
			sys.exit(1)
print '---'
print 'Darks are files',min(range(1,Darks+1)),'-',max(range(1,Darks+1))
print 'Pre-Flats are files',min(range(Darks+1,Darks+Flats+1)),'-',max(range(Darks+1,Darks+Flats+1))
print 'Projections are files',min(range(Darks+Flats+1,Darks+Flats+Projections+1)),'-',max(range(Darks+Flats+1,Darks+Flats+Projections+1))
print 'Post-Flats are files',min(range(Darks+Flats+Projections+1,Darks+Flats+Projections+Flats+1)),'-',max(range(Darks+Flats+Projections+1,Darks+Flats+Projections+Flats+1))
print '---'

# Copy (or actually symlink) the requested files
if options.darks:
	print 'Symlinking',Darks,'darks from',InputSample,'to',OutputSample
	if query_yes_no('Do you REALLY want to overwrite all darks?',default='no')=='yes':
		for Dark in range(1,Darks+1):
			linkcommand = 'ln -sf ' + os.path.join(InputPath,'tif',InputSample + "%.04d" % Dark + '.tif') + ' ' + os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Dark + '.tif')
			renamecommand = 'rename ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Dark + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif','_backup_' + OutputSample + "%.04d" % Dark + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Dark + '.tif')
			if options.verbose:
				print renamecommand
				print linkcommand
			if options.Test == False:
				os.system(renamecommand)
				os.system(linkcommand)
		print 'Done with symlinking',Darks,'darks from',InputSample,'to',OutputSample
	else:
		print 'Symlinking aborted'

if options.flats:
	print 'Symlinking',Flats,'pre- and',Flats,'post-flats from',InputSample,'to',OutputSample
	if query_yes_no('Do you REALLY want to overwrite the flats?',default='no')=='yes':
		for Flat in range(Darks+1,Darks+Flats+1):
			linkcommand = 'ln -sf ' + os.path.join(InputPath,'tif',InputSample + "%.04d" % Flat + '.tif') + ' ' + os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Flat + '.tif')
			renamecommand = 'rename ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Flat + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif','_backup_' + OutputSample + "%.04d" % Flat + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Flat + '.tif')
			if options.verbose:
				print renamecommand
				print linkcommand
			if options.Test == False:
				os.system(renamecommand)
				os.system(linkcommand)
		print 'Done with symlinking',Flats,'pre-flats from',InputSample,'to',OutputSample
		for Flat in range(Darks+Flats+Projections+1,Darks+Flats+Projections+Flats+1):
			linkcommand = 'ln -sf ' + os.path.join(InputPath,'tif',InputSample + "%.04d" % Flat + '.tif') + ' ' + os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Flat + '.tif')
			renamecommand = 'rename ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Flat + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif','_backup_' + OutputSample + "%.04d" % Flat + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Flat + '.tif')
			if options.verbose:
				print renamecommand
				print linkcommand
			if options.Test == False:
				os.system(renamecommand)
				os.system(linkcommand)
		print 'Done with symlinking',Flats,'post-flats from',InputSample,'to',OutputSample
	else:
		print 'Symlinking aborted'

if options.projections:
	print 'Symlinking',Projections,'projections from',InputSample,'to',OutputSample
	if query_yes_no('Do you REALLY want to overwrite the projections?',default='no')=='yes':
		for Projection in range(Darks+Flats+1,Darks+Flats+Projections+1):
			linkcommand = 'ln -sf ' + os.path.join(InputPath,'tif',InputSample + "%.04d" % Projection + '.tif') + ' ' + os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Projection + '.tif')
			renamecommand = 'rename ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Projection + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif','_backup_' + OutputSample + "%.04d" % Projection + '.tif') + ' ' +\
				os.path.join(OutputPath,'tif',OutputSample + "%.04d" % Projection + '.tif')
			if options.verbose:
				print renamecommand
				print linkcommand
			if options.Test == False:
				os.system(renamecommand)
				os.system(linkcommand)
		print 'Done with symlinking',Projections,'projections from',InputSample,'to',OutputSample
	else:
		print 'Symlinking aborted'

print
print 'Done!'
print
print 'You now probably want to recalculate the sinograms of'
print 'the Output-Sample with this command:'
print '    sinooff_tomcat_j.py',os.path.join(OutputPath,'tif')
