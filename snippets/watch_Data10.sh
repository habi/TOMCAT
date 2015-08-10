#!/bin/bash
# watch_Data10.sh | David Haberthür <david.haberthuer@psi.ch>
# Small bash snippet to view how much space is used on Data10.
# By "used" we mean only the stuff synched to the users HDs.
watch -n 600 "echo ---;du ~/Data10/disk* -sh --exclude-from ~/exclude.txt"
