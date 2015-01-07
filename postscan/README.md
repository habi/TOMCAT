# Postscan files

## StackedStanOverlap
Sometimes the overlap from starting a [[https://bitbucket.org/psitomcat/beamline-scripts/src/master/scan/stacked_scan.py][stacked scan]] is not what you expect it to be.
This is cumbersome to figure out after the fact.
That's the reason this script was born.
The script for finding overlap is available in the [[https://bitbucket.org/psitomcat/beamline-scripts/src/master/postscan/StackedScanOverlapFinder.py][beamline scripts repository]].

You start it with one mandatory parameter `-D` specifying the *first* of the several subscans (`Samplename_B1`).
The script then starts with sensible defaults for all parameters (enter '-h' to see them all).

It calculates the mean square error between the bottom reconstruction of stack N and some of the top reconstructions of stack N+1 (the '-p' option defines how many).
While it does that it shows you a nice picture, writes a log-file ('_stackedscan.merge.N.N+1.log') in the reconstructions directory of stack N+1.
After it's done, the script also saves an image with the result ('_stackedscan.merge.N.N+1.png').

Examples of this output are attached to this wiki page, the image below shows the process (quite a bit faster than in real life).

<img src="%ATTACHURLPATH%/StackedScanOverlap.gif" alt="StackedScanOverlap.gif" width='800' height='495' />

Once the script is done you should be able to figure out how to proceed from there...