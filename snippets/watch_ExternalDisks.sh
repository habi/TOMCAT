#!/bin/bash
# watch_ExternalDisks.sh | David Haberthür <david.haberthuer@psi.ch>
# Small bash snippet to view how much data is already synchronized to the disks.
# Should be run on the media station once the users HDs are conneted and syncing.
watch -n 600 "df -h /dev/sd?1"
