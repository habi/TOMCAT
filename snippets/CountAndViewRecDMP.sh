#!/bin/bash
# CountAndViewRecDMP.sh | David Haberthür <david.haberthuer@psi.ch>
# Small bash snippet to count the reconstructions and view one of them, iteratively for all subfolders.
for i in `ls */rec_DMP -d`;
do echo "Counting files contained in "$i"";
    COUNT=$(ls $i/ | wc -l);
    echo ""$i" contains "$COUNT" files, now looking at reconstructed slice 1280"
    sleep 3;
    fiji $i/*1280*;
    echo "--------------------------------"
done

