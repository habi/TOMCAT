#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
RetrieveFromArchivFTP.py | David Haberthür <david.haberthuer@psi.ch>

Script to retrieve a certain sample from the PSI tape archive
"""

import sys
from optparse import OptionParser
import getpass
import os
import subprocess

# Setup
MountPoint = '/archiv/project/sls'

# Setup the different options for the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-s', '--Sample', dest='Sample', type='str',
                  help='(incomplete) Name of the sample you would like to '
                  'retrieve from archivftp.psi.ch. *No* wildcard needed!',
                  metavar='R108C60')
parser.add_option('-e', '--eAccount', dest='eAccount', type='str',
                  help='eAccount in which I should look for (defaults to the '
                  'currently logged in user).',
                  metavar='e13960')
(options, args) = parser.parse_args()

# Show the help if necessary parameters are missing
if options.Sample is None:
    parser.print_help()
    print 'Example:'
    print 'The command below shows looks for all samples for which the name',\
        'contains C60 for the eAccount e11126 on the archive and downloads',\
        'them to subdirectories of the current directory.'
    print ''
    print sys.argv[0], '-e e11126 -s C60'
    print ''
    sys.exit(1)

if options.eAccount is None:
    options.eAccount = getpass.getuser()

# Go!
print 75 * '_'

print 'We are looking for samples containing "*' + options.Sample + '*".'
print
print 'For this I will start to look for files on',\
    os.path.join(MountPoint, options.eAccount), '(and ask you for the',\
    'password of the eAccount).'

# Generate command to list the files on the MountPoint on xbl-archiv
# From http://is.gd/ZVlIg9
sshCommand = 'ssh', '-q', options.eAccount + '@xbl-archiv', 'find',\
    os.path.join(MountPoint, options.eAccount), '-name', '\'*' +\
    options.Sample + '*\''

print
print 'I will use the command below to find what you are looking for'
print 'Until then: http://youtu.be/gY75dw64sqI'
print '---'
print ' '.join(sshCommand)
print '---'

sshProcess = subprocess.Popen(sshCommand, stdout=subprocess.PIPE)
SampleList = []
# Save all found samples in a list, so we can use them to present to the user
# http://stackoverflow.com/a/2813530/323100
while True:
    line = sshProcess.stdout.readline()
    if line.startswith(MountPoint):
        SampleList.append(line.rstrip())
    else:
        break
SampleList = sorted(SampleList)
print 75 * '_'

print 'In', os.path.commonprefix(SampleList) + '* I found:'
Counter = 0
for Sample in SampleList:
    # http://stackoverflow.com/a/11784589/323100
    print '    [' + str(Counter) + ']\033[1m', os.path.basename(Sample),\
        '\033[0min', os.path.dirname(Sample)
    Counter += 1

print 'Which sample should I get back from archivFTP?'
SampleNumberToGet = int(raw_input('Enter the sample number (from 0 to ' +
                                  str(Counter - 1) + '):'))
SampleToGet = SampleList[SampleNumberToGet]

print 75 * '_'

if not os.path.exists(os.path.basename(SampleToGet)):
    os.mkdir(os.path.basename(SampleToGet))
print
print 'Saving archivftp:' +\
    SampleToGet[len(os.path.commonprefix(SampleList)):], '/tif/TARCHIVE/'\
    'tif.tar to', os.path.abspath(SampleToGet), '/tif.tar'

rsyncCommand = 'rsync', '-arvhP', options.eAccount + '@xbl-archiv:' +\
    SampleToGet + '/tif/TARCHIVE/tif.tar',\
    os.path.abspath(os.path.basename(SampleToGet))

print
print 'I will use the command below to actually get back the tif.tar'
print '---'
print ' '.join(rsyncCommand)
print '---'
print 'This will take a (long) while'
subprocess.call(rsyncCommand)

print 75 * '_'

unpackCommand = 'tar', '-xvf',\
    os.path.join(os.path.abspath(os.path.basename(SampleToGet)), 'tif.tar')
print 'Now we unpack', os.path.abspath(os.path.basename(SampleToGet)) +\
    '/tif.tar to ./' + os.path.basename(SampleToGet) + '/tif/* by calling',\
    ' '.join(unpackCommand)

subprocess.call(unpackCommand)

print 75 * '_'
print 'All done for sample', os.path.basename(SampleToGet)
