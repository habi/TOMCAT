# TOMCAT

[![Code Health](https://landscape.io/github/habi/TOMCAT/master/landscape.svg)](https://landscape.io/github/habi/TOMCAT/master)

Scripts to ease some of the work at the TOMCAT beamline.
Mostly Python stuff which will obviously only work if you are at one of the X02DA consoles.
Most of the Python scripts give you some help if you start them without parameters, so it's a good idea to try that first.

## prescan 
These scripts are meant to be run before a scan is started and are used for alignment

## ImageJ macros
- [`CaptureRadiography.ijm`](prescan/CaptureRadiography.ijm) is an ImageJ macro to quickly capture a series of images.
    This image series is then saved to disk in a selected folder with a given pause betwen frames (useful for radiation damage/bubble creation studies or other such analyses).
    If exposure time is long this script will not take that into account and just have multiple copies of the same image.
    This is *much* less performant than the camera server.
- [`RadiographyAsStack.ijm`](prescan/RadiographyAsStack.ijm) also captures a series of images, but saves them into an ImageJ stack so they can be previewed immediately.
    This is limited by available memory in ImageJ.    

## Other handy things
- [`CenterAxis.py`](prescan/CenterAxis.py)` helps you to center the rotation axis.
    The calculations to do this are trivial, but annyoing to do over and over.
    If you use this script with the pins and image them first at 0° and 180° and then at 90° and 270° you should end up with a perfectly centered sample holder rotation axis.
    Starting the script without any parameters should give you a descriptive help.
- ```RadiographyAsStack.ijm``` is a script which can be run in the ImageJ control for the camera to capture a series of images from the camera and save them inside an ImageJ stack so they can be previewed immediately.
    This is limited by available memory in ImageJ.

## scan
These are scanning macros for use with [SPEC](http://www.certif.com/spec.html) and accompanying bash and Python scripts for running more complicated scans

- `fasttomo_edge_Aerotech.mac` is the standard tomography macro using end-station 1, the edge camera and the aerotech stage.
- `multiscan.py` is an example script for automating starting scans and changing sample names using epics channel interfaces. 

## postscan
These are scripts to run after the scan to perform reconstruction, center estimation, and other analyses.

## "Image" processing, viewing and assessing data
- ['ComputeSNR.py'`](postscan/ComputeSNR.py) can be used to calculate the Signal-to-Noise (or contrast-to-noise) ratio in images.
- [`multiscanViewer.py`](postscan/multiscanViewer.py) can be used to quockly view one reconstructed slice of several datasets.
- [`PaganinIterator.py`](postscan/PaganinIterator.py) can be used to (relatively) quickly submit a bunch of reconstructions with different δ and β values for the [Paganin phase retrieval](http://doi.org/10.1046/j.1365-2818.2002.01010.x).
  The script prepares the command-line calls to the SGE queue and submits them.
- [`PaganinPlotter.py`](postscan/PaganinPlotter.py) can be used to quickly plot said δ and β values from the [CXRO](http://henke.lbl.gov/optical_constants/) database.
- [`ReconstructSinogram.py`](postscan/ReconstructSinogram.py) reconstructs a single slice with the [SGE](http://en.wikipedia.org/wiki/Oracle_Grid_Engine) queue.
- [`ReplaceProjections.py`](postscan/ReplaceProjections.py) helps you to replace darks/flats/projections from one sample with the corresponding images from another sample, without doing any calculations about file numbers in your head.
- [`RotationCenterIterator.py`](postscan/RotationCenterIterator.py) calculates several rotation centers of a single slice.
  This is useful when the automatic center finding algorithm does not work and you'd like to quickly check several different rotation centers.
- [`SampleStatus.py`](postscan/SampleStatus.py) shows the status of all the samples measured, the number of projections/reconstructed slices, the estimated center, and center used for reconstruction.
    It is a useful way of keeping track of all the samples and which have been submitted and reconstruced already. 
- [`StackedScanOverlapFinder.py`](postscan/StackedScanOverlapFinder.py) helps you to define the overlap for stacked scan.
  Currently in beta and only in the `overlap detector` branch.

 
## Sample processing
- [`ManyScanReconHDF5.cmd`](postscan/ManyScanReconHDF5.cmd) is a command to reconstruct many samples to HDF5.
- [`missingSinoOff.cmd`](postscan/missingSinoOff.cmd) is a command to create sinograms for *all* folders that are missing them.
- [`pipelineRecon.bash`](postscan/pipelineRecon.bash) submits samples to the [SGE](http://en.wikipedia.org/wiki/Oracle_Grid_Engine) queue.

### Fast tomography
The `multi-*` family of files are used for reconstrucitons of datasets from fast tomography.
Ask Rajmund for details on those.

## Reconstruction

- The `grecoman` subfolder is a link to [Gorans Graphical Reconstruction Manager repository](https://github.com/gnudo/grecoman).
  Updated to his repositry can be pulled with `git submodule foreach git pull origin master && git pull bitbucket master && git submodule update --init --recursive`.
  This is done from time to time, so just checking out this repository recursively should lead to a workable state.

## Archival
- [`RetrieveFromArchivFTP.py`](postscan/RetrieveFromArchivFTP.py) helps you to get back a dataset from the [PSI tape archive](https://archivpsi.psi.ch).
  You give it a sample name and it gets the data back from you.
  A prerequisite is obviously that you *did* archive the data according to [our wiki page](https://intranet.psi.ch/wiki/bin/viewauth/Tomcat/Backups).

    
## snippets
These are small chunks of code (like gists) to use for various useful tasks at the beamline.
Some of the snippets (for convience) will be left on gist with hard links in the [README](README.md).

### Touch, Reconstruct, Compress, and Send via Email (https://gist.github.com/kmader/451d84937014b75368db)
These scripts can be used to touch (prevent deletion), perform reconstruction (using standard parameters), compress (into a single tar archive with up to 10x size improvements), and send using the Cifex system of ETH (up to 300GB/day, requires ETH login for sender but not reciever). 
