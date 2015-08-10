#!/bin/bash
# CountHowManySamples.sh | David Haberthür <david.haberthuer@psi.ch>
# Goes into each disk* directory, counts all folders (excluding log)
# and dumps the total number of folders.
for i in `ls ~/Data10/disk*/ -d`;
do COUNT=$(ls -d $i/*/ | grep -v log | wc -l);
echo $i contains $COUNT sample folders;
done
