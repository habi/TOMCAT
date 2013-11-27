#!/usr/bin/python

'''
Script to plot the delta and beta values foud in the [CXRO] database,
Get the data file from the [Index of Refraction] website, save it as NAME.dat
and plot it with this script

[CXRO]: http://henke.lbl.gov/optical_constants/
[Index of Refraction]: http://henke.lbl.gov/optical_constants/getdb2.html
'''

# First version: 2013-11-27

from optparse import OptionParser
import sys
import os
from pylab import *

# Use Pythons Optionparser to define and read the options, and also
# give some help to the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-f', '--file', dest='DataFile',
                  help='File you saved as NAME.dat from the CXRO database. '
                       'I will plot the data in this file for you.',
                  metavar='path/file.dat')
parser.add_option('-d', '--Delta', dest='Delta',
                  default=False, action='store_true',
                  help='Plot *only* Delta. By default the script is plotting '
                       'both delta and beta')
parser.add_option('-b', '--Beta', dest='Beta',
                  default=False, action='store_true',
                  help='Plot *only* Beta. By default the script is plotting '
                       'both delta and beta')
(options, args) = parser.parse_args()

# show the help if no parameters are given
if options.DataFile is None:
    parser.print_help()
    print 'Example:'
    print 'help'
    print
    print sys.argv[0], ('-f path/file.dat')
    print
    sys.exit(1)

if os.path.exists(os.path.abspath(options.DataFile)) is not True:
    print 'I was not able to find', os.path.abspath(options.DataFile)
    print 'Please try again with the correct path or existing file...'
    print
    sys.exit(1)

Data = loadtxt(options.DataFile, skiprows=2)

plt.figure()
if not options.Beta:
    plt.loglog(Data[:, 0], Data[:, 1], label='Delta')
if not options.Delta:
    plt.loglog(Data[:, 0], Data[:, 2], label='Beta')
if options.Delta:
    plt.ylabel('Delta')
if options.Beta:
    plt.ylabel('Beta')
if not options.Delta and not options.Beta:
    plt.ylabel('Delta/Beta')
plt.title(' '.join([os.path.basename(options.DataFile),
                    '- red region = TOMCATs range']))
plt.xlabel('Photon Energy [eV]')
plt.axvspan(8000, 45000, facecolor='r', alpha=0.5)
plt.xlim([min(Data[:, 0]), max(Data[:, 0])])
plt.legend(loc=3)

plt.show()
