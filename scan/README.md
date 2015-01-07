# Scanning stuff
These are scanning macros for use with [SPEC](http://www.certif.com/spec.html) and accompanying bash and Python scripts for running more complicated scans.

- [`fasttomo_edge_Aerotech.mac`]() is the standard tomography macro using end-station 1, the [pco.edge camera](http://www.pco.de/scmos-cameras/) and the [Aerotech rotation stage](http://www.aerotech.com/).
- [`multiscan.py`]() is an example script for automating starting scans and changing sample names using [EPICS](http://www.aps.anl.gov/epics/) channel interfaces.
- [`stacked_scan.py`]() can be used to perform multiple overlapping scans along the rotation axis of the sample.

