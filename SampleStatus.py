#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Script to show the samples currently measured, basic information about them (center, etc), and how many files are in each of the
corresponding directories. 
'''

# Import necessary modules
from glob import glob
from optparse import OptionParser
from os import getlogin
import os,sys
globals()['errorLog']=[]
def errorMsg(x): globals()['errorLog']+=[x]

args=OptionParser()
args.add_option('-u','--user',dest='user',default=getlogin(),help='Username to search')
args.add_option('-s','--stdrec',dest='stdrec',default='rec_8bit',help='Standard reconstruction name')
args.add_option('-p','--pagrec',dest='pagrec',default='rec_8bit_pag',help='Standard paganin reconstruction name')
(opts,other)=args.parse_args()

rootPath='/sls/X02DA/data/'+opts.user+'/'
cRecFunc=lambda sufx: glob(rootPath+'Data10/*/*/'+sufx)+glob(rootPath+'Data20/*/*/'+sufx)
remRecFunc=lambda fName: ('/'.join(fName.split('/')[:-1]) , fName.split('/')[-1])
# A,B,C are so the results are ordered correctly when using sorted before printing
folders={'tif':'A:Projs','fltp':'B:SinoffPag','rec_8bit_pag':'C:PhaseRecon','rec_8bit_abs':'C:AbsRecon','rec_8bit_nrm':'C:NrmRecon','rec_8bit':'C:Std.Recon8','rec_16bit':'C:Std.Recon16'}
folders[opts.stdrec]='C:Std.Recon'
folders[opts.pagrec]='C:Pag.Recon'
allfiles=reduce(lambda a,b: a+b,map(cRecFunc,folders.keys())) # make a flat list of all the keys
allsamples={}
for cfile in allfiles:
   (cfold,csx)=remRecFunc(cfile)
   allsamples[cfold]=allsamples.get(cfold,[])+[csx]

def getRot(foldName): # get the rotation center from the log file
   try:
      curLog=glob(foldName+'/tif/*.log')[0]
      f=open(curLog)
      cCenter=filter(lambda line: line.find('Rotation center:')>=0,f.readlines())[-1].strip()
      try:
         return 'EstRotCent'.join(cCenter.split('Rotation center'))+' :'
      except:
         # Center line not found (don't report is just means sinoff/sinfly has not been run yet
         return ''
   except:
      errorMsg(foldName+' log not found!')
      return ''


def fixFolderName(cFolder,cSuffix):
   newSuffix=folders.get(cSuffix,cSuffix)
   return newSuffix+'('+str(len(glob(cFolder+'/'+cSuffix+'/*')))+')'

for cfold in sorted(allsamples.keys()):
   cSubDirs=allsamples[cfold]
   cNamed=sorted(map(lambda fn: fixFolderName(cfold,fn),cSubDirs))
   print '/'.join(cfold.split('/')[-3:])+':'+getRot(cfold)+str(cNamed)

eLog=globals()['errorLog']
if len(eLog)>0:
   print '\n'.join(['Error(s) Found']+eLog)