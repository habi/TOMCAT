# TOMCAT

Scripts to ease some of the work at the TOMCAT beamline.
Mostly Python stuff which will obviously only work if you are at one of the
X02DA consoles...

## prescan 
These scripts are meant to be run before a scan is started and are used for alignment

- ```CaptureRadiography.ijm``` is a script which can be run in the ImageJ control for the camera to capture a series of images.
    This image series is then saved to disk in a selected folder with a given pause betwen frames (useful for radiation damage/bubble creation studies or other such analyses).
    If exposure time is long this script will not take that into account and just have multiple copies of the same image.
    This is much less performant than the camera server.
- ```CenterAxis.py``` helps you to center the rotation axis.
    The calculations to do this are trivial, but annyoing.
    If you use this script with the pins and image them first at 0° and 180° and then at 90° and 270° you should end up with a perfectly centered sample holder rotation axis.
    Starting the script without any parameters should give you a descriptive help.
- ```RadiographyAsStack.ijm``` is a script which can be run in the ImageJ control for the camera to capture a series of images from the camera and save them inside an ImageJ stack so they can be previewed immediately.
    This is limited by available memory in ImageJ.

## scan
These are scanning macros for use with spec and accompanying bash and python scripts for running more complicated scans

- ```fasttomo_edge_Aerotech.mac``` is the standard tomography macro using end-station 1, the edge camera and the aerotech stage
- ```multiscan.py``` is an example script for automating starting scans and changing sample names using epics channel interfaces. 

## postscan
These are scripts to run after the scan to perform reconstruction, center estimation, and other analyses.

- ```SampleStatus.py``` shows the status of all the samples measured, the number of projections/reconstructed slices, the estimated center, and center used for reconstruction.
    It is a useful way of keeping track of all the samples and which have been submitted and reconstruced already. 
- ```PaganinIterator.py``` makes it easy to calculate the Paganin phase retrieval reconstructions with several orders of magnitude of delta and beta.
    The script prepares the command-line calls to the SGE queue and submits them.
    Starting the script without any parameters should give you a descriptive help.
- ```ReplaceProjections.py``` helps you to replace darks/flats/projections from one sample with the corresponding images from another sample, without doing any calculations about file numbers in your head.
- ```RotationCenterIterator.py``` calculates several rotation centers of a single slice.
    This is useful when the automatic center finding algorithm does not work and you'd like to quickly check several different rotation centers.
    Starting the script without any parameters should give you a descriptive help.
- The ```grecoman``` subfolder is a link to [Gorans Graphical Reconstruction Manager repository](https://github.com/gnudo/grecoman).
    Updated to his repositry can be pulled with ```git submodule foreach git pull origin master && git pull bitbucket master && git submodule update --init --recursive```.
    This is done from time to time, so just checking out this repository recursively should lead to a workable state.
    
## snippets
These are small chunks of code (like gists) to use for various useful tasks at the beamline. Some of the snippets (for convience will be left on gist with hard links in the readme).
### Touch, Reconstruct, Compress, and Send via Email (https://gist.github.com/kmader/451d84937014b75368db)
These scripts can be used to touch (prevent deletion), perform reconstruction (using standard parameters), compress (into a single tar archive with up to 10x size improvements), and send using the Cifex system of ETH (up to 300GB/day, requires ETH login for sender but not reciever). 