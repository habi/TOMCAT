#!/bin/bash
# remove-easily-regenerated-folders.sh | David Haberthür <david.haberthuer@psi.ch>
# Removes all easily regenerated folders in all subfolders.
# Corrected and filtered projections, sinograms and RecoManager GUI files are deleted.
# Asking the user is based on http://stackoverflow.com/a/226724
CURRENTFOLDER=$(pwd)
echo "Do you wish to remove all cpr, fltp, sin and viewrec folders in all
subfolders of $CURRENTFOLDER?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) 	
		echo "removing $CURRENTFOLDER/*/cpr*";
		sleep 3;
		for i in `ls * -d`;
			do du -sh $i/cpr*;
		done;
		echo;
		echo "removing $CURRENTFOLDER/*/fltp*";
		sleep 3;		
		for i in `ls * -d`;
			do du -sh $i/cpr*;
		done;
		echo;
		echo "removing $CURRENTFOLDER/*/sin*";
		sleep 3;		
		for i in `ls * -d`;
			do du -sh $i/sin*;
		done;
		echo;
		echo "removing $CURRENTFOLDER/*/viewrec*";
		sleep 3;		
		for i in `ls * -d`;
			do du -sh $i/viewrec*;
		done;		
		break;;
        No ) echo "Phew, that was close!";exit;;
    esac
done
