# TOMCAT

Scripts to ease some of the work at the TOMCAT beamline.
Mostly Python stuff which will obviously only work if you are at one of the
X02DA consoles...

## prescan 
These scripts are meant to be run before a scan is started and are used for alignment

- ```CaptureRadiography.ijm``` 
is a script which can be run in the ImageJ control for the camera to capture a series of images from the camera and save them to disk in a selected folder with a given pause betwen frames (useful for radiation damage / bubble creation studies or other such analyses). If exposure time is long this script will not take that into account and just have multiple copies of the same image. This is much less performant than the camera server.
- ```RadiographyAsStack.ijm``` 
is a script which can be run in the ImageJ control for the camera to capture a series of images from the camera and save them inside an ImageJ stack so they can be previewed immediately. This is limited by available memory in ImageJ.


## scan
These are scanning macros for use with spec and accompanying bash and python scripts for running more complicated scans

- ```fasttomo_edge_Aerotech.mac``` 
is the standard tomography macro using end-station 1, the edge camera and the aerotech stage
- ```multiscan.py``` 
is an example script for automating starting scans and changing sample names using epics channel interfaces. 

## postscan
These are scripts to run after the scan to perform reconstruction, center estimation, and other analyses.

- ```SampleStatus.py``` 
shows the status of all the samples measured, the number of projections / reconstructed slices, the estimated center, and center used for reconstruction. 
It is a useful way of keeping track of all the samples and which have been submitted and reconstruced already. 

## snippets
These are small chunks of code (like gists) to use for various useful tasks at the beamline