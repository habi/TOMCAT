#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Script to reduce the size of a pdf, handy for emailing to collaborators
Based on command found on http://www.ehow.com/how_6823473_reduce-pdf-file-size-
linux.html
First version 22.01.2013, David Haberthür
Second version 07.05.2013, David Haberthür: Cleanup
'''

from optparse import OptionParser
import sys
import os

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-i', '--Input', dest='InputFile',
                  help='Input File, with (relative) path',
                  metavar='SomeFile.pdf')
parser.add_option('-o', '--Output', dest='OutputFile',
                  help='Optional output file name. '
                  'Default=InputFile_quality.pdf',
                  metavar='SomeName')
parser.add_option('-q', '--Quality', dest='Quality',
                  help='Optional quality parameter. Default is "screen", '
                  'others are "ebook", "printer" and "prepress", in ascending '
                  'order of quality',
                  metavar='printer', default='screen')
'''
Quality level settings are "/screen," the lowest resolution and lowest file
size, but fine for viewing on a screen; "/ebook," a mid-point in resolution and
file size; "/printer" and "/prepress," high-quality settings used for printing
PDFs.
'''
(options, args) = parser.parse_args()

if options.InputFile is None:
    parser.print_help()
    print 'Example:'
    print 'The command below Print example'
    print ''
    print sys.argv[0], '-i SomeDir/SomeFile.pdf'
    print ''
    sys.exit(1)

if options.OutputFile:
    OutputName = os.path.join(os.path.dirname(options.InputFile),
                              options.OutputFile + '.pdf').replace(' ', '\ ')
else:
    OutputName = os.path.splitext(options.InputFile)[0].replace(' ', '\ ') + \
        '_' + options.Quality + '.pdf'

print
if options.Quality in ('screen', 'ebook', 'printer', 'prepress'):
    print 'Converting'
    print options.InputFile
    print 'to the', options.Quality + '-quality PDF'
    print OutputName
else:
    print 'You probably have a ypot in the quality settings. :)'
    print 'You can only enter one of these:'
    print '    -q screen (default)'
    print '    -q ebook'
    print '    -q printer'
    print '    -q prepress'
    print
    print 'Please try again!'
    sys.exit(1)

reducecommand = 'gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite ' + \
    '-dCompatibilityLevel=1.4 -dPDFSETTINGS=' + '/' + options.Quality + \
    ' -sOutputFile=' + OutputName + ' ' + \
    options.InputFile.replace(' ', '\ ') + '> /dev/null'

os.system(reducecommand)
print 'done'
