#! /bin/bash
# usage: pipelineRecon.bash diskName sampleName
# runs runs the standard absorption reconstruction using the new pipeline with the following settings
# saves the files as 16 bit tiff files
eaccount=$USER
disk=$1
name=$2
Np=1501
Nd=80
Nf=200
MINV="-0.003"
MAXV="0.003"


sgeCommand="prj2sinSGE -I 1 -d -f $Np,$Nd,$Nf,0,0 -R 1 -F parz -Z 0.5 -t 16 -n $MINV -x $MAXV -L 1 -p $name####.tif -o /sls/X02DA/data/$eaccount/Data10/$disk/$name/sin/ /sls/X02DA/data/$eaccount/Data10/$disk/$name/tif/"
echo "Submitting: $sgeCommand"

$sgeCommand
sleep 1


