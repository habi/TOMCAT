# Post-scan scripts
## "Image" processing, viewing and assessing data
- [`ComputeSNR.py`](ComputeSNR.py) can be used to calculate the Signal-to-Noise (or contrast-to-noise) ratio in images.
- [`multiscanViewer.py`](multiscanViewer.py) can be used to quickly view one reconstructed slice of several data sets.
- [`PaganinIterator.py`](PaganinIterator.py) can be used to (relatively) quickly submit a bunch of reconstructions with different δ and β values for the [Paganin phase retrieval](http://doi.org/10.1046/j.1365-2818.2002.01010.x).
  The script prepares the command-line calls to the SGE queue and submits them.
- [`PaganinPlotter.py`](PaganinPlotter.py) can be used to quickly plot said δ and β values from the [CXRO](http://henke.lbl.gov/optical_constants/) database.
- [`ReconstructSinogram.py`](ReconstructSinogram.py) reconstructs a single slice with the [SGE](http://en.wikipedia.org/wiki/Oracle_Grid_Engine) queue.
- [`ReplaceProjections.py`](ReplaceProjections.py) helps you to replace darks/flats/projections from one sample with the corresponding images from another sample, without doing any calculations about file numbers in your head.
- [`RotationCenterIterator.py`](RotationCenterIterator.py) calculates several rotation centers of a single slice.
  This is useful when the automatic center finding algorithm does not work and you'd like to quickly check several different rotation centers.
- [`SampleStatus.py`]() shows the status of all the samples measured, the number of projections/reconstructed slices, the estimated center, and center used for reconstruction.
    It is a useful way of keeping track of all the samples and which have been submitted and reconstructed already. 
- [`StackedScanOverlapFinder.py`](StackedScanOverlapFinder.py) helps you to define the overlap for stacked scan.
  Sometimes the overlap from starting a [stacked scan](../scan/stacked_scan.py)] is not what you expect it to be.
  This is cumbersome to figure out after the fact.
  You start it with one mandatory parameter `-D` specifying the *first* of the several subscans (`Samplename_B1`).
  The script then starts with sensible defaults for all parameters (use the `-h`-option to see them all).

  It calculates the mean square error between the bottom reconstruction of stack *N* and some of the top reconstructions of stack *N+1* (the `-p` option defines how many).
  While it does that it shows you a nice picture, writes a log-file (`_stackedscan.merge.N.N+1.log`) in the reconstructions directory of stack *N+1*.
  After it's done, the script also saves an image with the result (`_stackedscan.merge.N.N+1.png`).
  Once the script is done you should be able to figure out how to proceed from there...
  
  ![Running script](http://f.cl.ly/items/1U082A2m1N0w2H1b0U0T/StackedScanOverlap.gif)

## Sample processing
- [`ManyScanReconHDF5.cmd`](ManyScanReconHDF5.cmd) is a command to reconstruct many samples to HDF5.
- [`missingSinoOff.cmd`](missingSinoOff.cmd) is a command to create sinograms for *all* folders that are missing them.
- [`pipelineRecon.bash`](pipelineRecon.bash) submits samples to the [SGE](http://en.wikipedia.org/wiki/Oracle_Grid_Engine) queue.

### Fast tomography
The `multi-*` family of files are used for reconstructions of datasets from fast tomography.
Ask Rajmund for details on those.

## Reconstruction
- The `grecoman` subfolder is a link to [Gorans Graphical Reconstruction Manager repository](https://github.com/gnudo/grecoman).
  Updates to his repository can be pulled with `git submodule foreach git pull origin master && git pull bitbucket master && git submodule update --init --recursive`.
  This is done from time to time, so just checking out this repository recursively should lead to a workable state.

## Archival
- [`RetrieveFromArchivFTP.py`](RetrieveFromArchivFTP.py) helps you to get back a dataset from the [PSI tape archive](https://archivpsi.psi.ch).
  You give it a sample name and it gets the data back from you.
  A prerequisite is obviously that you *did* archive the data according to [our wiki page](https://intranet.psi.ch/wiki/bin/viewauth/Tomcat/Backups).
  
  
  

