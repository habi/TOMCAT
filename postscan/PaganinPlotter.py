#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
PaganinPlotter.py | David Haberthür <david.haberthuer@psi.ch>

Script to plot the delta and beta values foud in the [CXRO] database,
Get the data file from the [Index of Refraction] website, save it as NAME.dat
and plot it with this script

[CXRO]: http://henke.lbl.gov/optical_constants/
[Index of Refraction]: http://henke.lbl.gov/optical_constants/getdb2.html
'''

# 2013-11-27: First version:
# 2013-11-28: Updated to show selected values

from optparse import OptionParser
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

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
parser.add_option('-s', '--Save', dest='Save',
                  default=False, action='store_true',
                  help='Save plot as NAME.pdf in current directory (default: '
                       '%default)')
parser.add_option('-e', '--Energy', dest='Energy',
                  type=float, default=20., metavar=12.9,
                  help='Energy [keV] you would like to know Delta and Beta '
                       '(default: %default)')
parser.add_option('-t', '--tomcat', dest='TOMCAT',
                  default=False, action='store_true',
                  help='Plot only TOMCAT-range of Energies (default: '
                       '%default)')
parser.add_option('--png', dest='png',
                  default=False, action='store_true',
                  help='Save plot as .png (default: .pdf)')
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

# Inform user if we cannot find data file, otherwise load it
if os.path.exists(os.path.abspath(options.DataFile)) is not True:
    print 'I was not able to find', os.path.abspath(options.DataFile)
    print 'Please try again with the correct path or existing file...'
    print
    print 'Maybe you first need to download a data file. For this, go to'
    print 'http://henke.lbl.gov/optical_constants/getdb2.html'
    print 'enter a chemical formula and request a "Text File", then save it',\
        'somewhere.'
    print
    sys.exit(1)
Data = np.loadtxt(options.DataFile, skiprows=2)
# Convert the ndarray to lists for simpler handling
Energy = Data[:, 0].tolist()
Delta = Data[:, 1].tolist()
Beta = Data[:, 2].tolist()

# Get the closest to the chosen energy and show values around that to the user.
# http://stackoverflow.com/a/9706105/323100
ClosestEnergy = Energy[min(range(len(Energy)),
                       key=lambda i:abs(Energy[i] - options.Energy*1000))]
print
print 'For',
if options.Energy == 20.:
    print 'a default',
else:
    print 'the chosen',
print 'value of', options.Energy, 'keV, the closest value found in',\
    os.path.basename(options.DataFile), 'is', round(ClosestEnergy) / 1000,\
    'keV'
print 'The values around this energy are:'
print '    *', round(Energy[Energy.index(ClosestEnergy)-1]) / 1000,\
    'keV, with',
CurrentDelta = Delta[Energy.index(ClosestEnergy)-1]
CurrentBeta = Beta[Energy.index(ClosestEnergy)-1]
print 'a Delta of', "%.4g" % CurrentDelta, 'and a Beta of',\
    "%.4g" % CurrentBeta

print '    *', round(Energy[Energy.index(ClosestEnergy)]) / 1000, 'keV, with',
CurrentDelta = Delta[Energy.index(ClosestEnergy)]
CurrentBeta = Beta[Energy.index(ClosestEnergy)]
print 'a Delta of', "%.4g" % CurrentDelta, 'and a Beta of',\
    "%.4g" % CurrentBeta

# Plot Delta and/or Beta
plt.figure()
if not options.Beta:
    plt.loglog(Energy, Delta, 'g', label='Delta')
if not options.Delta:
    plt.loglog(Energy, Beta, 'b', label='Beta')
if options.Delta:
    plt.ylabel('Delta')
if options.Beta:
    plt.ylabel('Beta')
if not options.Delta and not options.Beta:
    plt.ylabel('Delta/Beta')
PlotTitle = os.path.basename(options.DataFile)

# Plot the closest value found
PlotTitle += '\nEnergy=' + str(round(ClosestEnergy) / 1000) + ' keV, Delta=' +\
    str("%.4g" % CurrentDelta) + ', Beta=' + str("%.4g" % CurrentBeta)
plt.plot(ClosestEnergy, CurrentDelta, 'go')
plt.plot(ClosestEnergy, CurrentBeta, 'bo')
plt.title(PlotTitle)
if not options.TOMCAT:
    plt.axvspan(8000, 45000, facecolor='r', alpha=0.5)
    plt.xlim([min(Energy), max(Energy)])
    plt.legend(loc=3)
    plt.xlabel('Photon Energy [eV] | red region = TOMCATs range')
else:
    plt.xlim([8e3, 45e3])
    plt.legend(loc='best')
    plt.xlabel('Photon Energy [eV] | TOMCAT: 8-45 keV')

print '    * and', round(Energy[Energy.index(ClosestEnergy)-1]) / 1000,\
    'keV, with',
CurrentDelta = Delta[Energy.index(ClosestEnergy)+1]
CurrentBeta = Beta[Energy.index(ClosestEnergy)+1]
print 'a Delta of', "%.4g" % CurrentDelta, 'and a Beta of',\
    "%.4g" % CurrentBeta

if options.Save:
    filename = os.path.splitext(os.path.abspath(options.DataFile))[0]
    if options.png:
        filename += '.png'
    else:
        filename += '.pdf'
    plt.savefig(filename)
    print 'Saved plot to', filename
else:
    plt.show()
