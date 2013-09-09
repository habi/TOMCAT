#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Script to remove the first page of a pdf.
Based on a command found on http://cilab.math.upatras.gr/mikeagn/content/how-
extract-pages-multiple-page-pdf-file
First version: 07.05.2013, David Haberthür
'''

from optparse import OptionParser
import sys
import os
import subprocess

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-i', '--Input', dest='InputFile',
                  help='Input File, with (relative) path',
                  metavar='SomeFile.pdf')
parser.add_option('-o', '--Output', dest='OutputFile',
                  help='Optional output file name. '
                  ' Default=InputFile_stripped.pdf',
                  metavar='SomeName')
(options, args) = parser.parse_args()

if options.InputFile is None:
    parser.print_help()
    print 'Example:'
    print 'The command below removes the first page of SomeFile.pdf'
    print ''
    print sys.argv[0], '-i SomeDir/SomeFile.pdf'
    print ''
    sys.exit(1)

if not os.path.exists(options.InputFile):
    print 'I cannot find the input file, try again with correct path.'
    sys.exit(1)

if options.OutputFile:
    OutputName = os.path.join(os.path.dirname(options.InputFile),
                              options.OutputFile).replace(' ', '\ ')
else:
    OutputName = os.path.splitext(options.InputFile)[0].replace(' ', '\ ') + \
        '_stripped.pdf'

print

# Use 'pdfinfo' to find how many pages we have
# http://stackoverflow.com/a/3503909
Information = subprocess.Popen(['pdfinfo ' + options.InputFile],
                               stdout=subprocess.PIPE, shell=True)
(Output, Error) = Information.communicate()
NumberOfPages = int(Output[Output.find('Pages'):
                    Output.find('Encrypted')].split(' ')[-1])

# Strip first page
removecommand = 'gs -sDEVICE=pdfwrite -dNOPAUSE -dBATCH -dSAFER ' + \
    '-dFirstPage=2 -dLastPage=' + str(NumberOfPages) + ' -sOutputFile=' +\
    OutputName + ' ' + options.InputFile + '> /dev/null'

print 'Stripping first page of', options.InputFile, 'with the'
print removecommand
print
os.system(removecommand)
print
print 'done'
