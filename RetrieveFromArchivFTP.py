#!/usr/bin/python

'''
Script to retrieve a certain sample from the archive
'''
import sys
from optparse import OptionParser
import getpass
import os
import subprocess

# Setup
MountPoint = '/mnt/archiv/project/sls'

# Setup the different options for the user
parser = OptionParser()
usage = "usage: %prog [options] arg"
parser.add_option('-s', '--Sample', dest='Sample', type='str',
                  help='(incomplete) Name of the sample you would like to '
                  'retrieve from archivftp.psi.ch',
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
    print 'The command below shows looks for all samples R108C60* for the',\
        'eAccount e11126 on the archive and downloads them to subdirectories',\
        'of the current directory.'
    print ''
    print sys.argv[0], '-e e11126 -s R108C60'
    print ''
    sys.exit(1)

if options.eAccount is None:
    options.eAccount = getpass.getuser()

# Go!
print 80 * '_'

print 'We are looking for sample "' + options.Sample + '*" on x02da-cn-6.'
print
print 'For this I will start to look for files on',\
    os.path.join(MountPoint, options.eAccount), '(and ask you for the',\
    'password of the eAccout).'


# Generate command to list the files on the MountPoint on x02da-cn-6
# From http://is.gd/ZVlIg9
sshCommand = 'ssh -q', options.eAccount + '@x02da-cn-6 \'find',\
    os.path.join(MountPoint, options.eAccount), '-name', options.Sample + '*\''
sshCommand = ' '.join(sshCommand)

print
print 'I will use the command below to find what you are looking for'
print '---'
print sshCommand
print '---'

process = subprocess.Popen(sshCommand, stdout=subprocess.PIPE, shell=True)
SampleList = []
# Save all found samples in a list, so we can use them lateron to present
# to the user: http://stackoverflow.com/a/2813530/323100
while True:
    line = process.stdout.readline()
    if line.startswith(MountPoint):
        SampleList.append(line.rstrip())
    else:
        break

print 80 * '_'

print 'In', os.path.commonprefix(SampleList), 'I found:'
Counter = 0
for Sample in SampleList:
    # http://stackoverflow.com/a/11784589/323100
    print '    [' + str(Counter) + ']\033[1m',  os.path.basename(Sample),\
        '\033[0min',\
        os.path.dirname(Sample)[len(os.path.commonprefix(SampleList)):]
    Counter += 1

print 'Which sample should I get back from archivFTP?'
SampleNumberToGet = int(raw_input('Enter the sample number (from 0 to ' +
                                  str(Counter - 1) + '):'))
SampleToGet = SampleList[SampleNumberToGet]

print 80 * '_'

if not os.path.exists(os.path.basename(SampleToGet)):
    os.mkdir(os.path.basename(SampleToGet))
print
print 'Saving archivftp:' +\
    SampleToGet[len(os.path.commonprefix(SampleList)):], '/tif/TARCHIVE/'\
    'tif.tar to', os.path.abspath(SampleToGet), '/tif.tar'

rsyncCommand = 'rsync -arvhP', options.eAccount + '@x02da-cn-6:' +\
    SampleToGet + '/tif/TARCHIVE/tif.tar',\
    os.path.abspath(os.path.basename(SampleToGet))
rsyncCommand = ' '.join(rsyncCommand)

print
print 'I will use the command below to actually get back the tif.tar'
print '---'
print rsyncCommand
print '---'
print 'This will take a (long) while'
process = subprocess.Popen(rsyncCommand, stdout=subprocess.PIPE, shell=True)

print 80 * '_'

print 'Now we can unpack', os.path.abspath(os.path.basename(SampleToGet)) +\
    '/tif.tar to ./' + os.path.basename(SampleToGet) + '/tif/*'
os.chdir(os.path.abspath(os.path.basename(SampleToGet)))
process = subprocess.Popen('tar -xvf tif.tar', stdout=subprocess.PIPE,
                           shell=True)
