#!/usr/bin/python

'''
Script to reconstruct a sample with different Paganin parameters.
Very loosely based on Peter Modreggers 'pags' bash script
'''

# First version: 2013-02-18: Based on ReconstructSinogram.py

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
parser.add_option('-d', '--Delta', dest='Delta', type = 'float',
	help='Delta you want to start with',
	metavar='3e-10')
parser.add_option('-b', '--Beta', dest='Beta', type='float',
	help='Beta you want to start with',
	metavar='3e-10')
parser.add_option('-z', dest='Distance', default=50, type='int',
	help='Distance to the scintillator in mm',
	metavar=33)
parser.add_option('-r', '--range', dest='Range', type='int',
	help='Range of powers you want to iterate through',
	metavar='3')
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
	print 'please enter a Delta value with the -d parameter'
	sys.exit(1)
	
if options.Beta is None:
	print 'please enter a Beta value with the -b parameter'
	sys.exit(1)
	
if options.Range is None:
	print 'please enter a range you want to iterate over with the -r parameter'
	sys.exit(1)	

# Assemble Directory- and Samplenames and prepare all other parameters
## test if the directory exists, if not, tell the user
if os.path.exists(options.SampleFolder) is False:
	print
	print 'Directory "' + options.SampleFolder + '" not found, please try again with full (and correct) path.'
	print
try:
	SampleFolder = os.path.basename(os.path.dirname(os.path.abspath(options.SampleFolder)))
	# abspath "converts" trailing backslash or not to a nice path, getting
	# rid of relative pathnames. The dirname wrapped around it gets rid 
	# of the Sin-Directory and the additional basename around it extracts
	# the Directory-name of the sample.
except:
	print 'I was not able to deduce a SampleFolder from your input.'
	print "Please specify a path like this './SampleFolder/' with the '-D'-option."
	print 'It is probably best if you try again with the absolute path...'
	
if options.Test:
	print 'I would do this'

for i in range(-options.Range,options.Range+1):
	Delta = float(str('%e' % options.Delta)[:-2] + str(int(str('%e' % options.Delta)[-2:]) + i))
	# Construct Paganin-call
	ReconstructionCommand = ' '.join(['~/scripts/sinooff_tomcat_paganin.py',os.path.abspath(os.path.join(options.SampleFolder,'tif')),str(Delta),str(options.Beta),str(options.Distance)])
	MoveSinogramsCommand = ' '.join(['mv',os.path.abspath(os.path.join(options.SampleFolder,'sin')),os.path.abspath(os.path.join(options.SampleFolder,'sin_' + str(Delta) + '_' + str(options.Beta)))])
	MoveFilteredProjectionsCommand = ' '.join(['mv',os.path.abspath(os.path.join(options.SampleFolder,'fltp')),os.path.abspath(os.path.join(options.SampleFolder,'fltp_' + str(Delta) + '_' + str(options.Beta)))])
	if options.Test:
		print ReconstructionCommand
		print MoveSinogramsCommand
		print MoveFilteredProjectionsCommand
		print 80 * '_'
	else:
		print 'Reconstructing'
		print os.system(ReconstructionCommand)
		print 'Renaming sinogram folder'
		print os.system(MoveSinogramsCommand)
		print 'Renaming filtered projections folder'
		print os.system(MoveFilteredProjectionsCommand)

if options.Test:
	print 'I was just testing'
else:
	print 'Done with what you have asked for.'
	print
	print 'You now have the Sinogram-Directories'
	for i in range(-options.Range,options.Range+1):
		Delta = float(str('%e' % options.Delta)[:-2] + str(int(str('%e' % options.Delta)[-2:]) + i))
		print '    *',os.path.abspath(os.path.join(options.SampleFolder,'sin_' + str(Delta) + '_' + str(options.Beta)))
	print 'Use ReconstructSinogram.py for each of those to actually recostruct a slice'
