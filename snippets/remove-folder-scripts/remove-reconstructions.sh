#!/bin/bash
# remove-reconstructions.sh | David Haberthür <david.haberthuer@psi.ch>
# Removes all rec*-folders in all subfolders.
# Also asks the user twice :)
# Asking the user is based on http://stackoverflow.com/a/226724
CURRENTFOLDER=$(pwd)
echo "Do you wish to remove all reconstructions in all subfolders of $CURRENTFOLDER?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) 	
		echo "removing $CURRENTFOLDER/*/rec*";
		sleep 3;
		echo "Just kidding...";
		sleep 1;
		echo "Are you really sure?"
		select yn in "Yes" "No"; do
		    case $yn in
		        Yes ) 	
				echo "OK, you asked for it!";
				echo "removing $CURRENTFOLDER/*/rec*";
				for i in `ls * -d`;
					do du -sh $i/rec*;
				done;
				break;;
		        No ) echo "OK, bye!";exit;;
		    esac
		done
		break;;
        No ) echo "Phew, that was close!";exit;;
    esac
done
