# TOMCAT

[![Code Health](https://landscape.io/github/habi/TOMCAT/master/landscape.svg)](https://landscape.io/github/habi/TOMCAT/master)

Scripts to ease some of the work at the TOMCAT beamline.
Mostly Python stuff which will obviously only work if you are at one of the X02DA consoles.
Most of the Python scripts give you some help if you start them without parameters, so it's a good idea to try that first.

## Pre-scan stuff
These scripts are meant to be run before a scan is started and are used for alignment.
Take a look at the [`README`](prescan/README.md) in the [prescan subfolder](prescan) for an explanation of each file.

## Scripts for scanning
These are scanning macros for use with [SPEC](http://www.certif.com/spec.html) and accompanying bash and Python scripts for running more complicated scans.
Take a look at the [`README`](scan/README.md) in the [scan subfolder](scan) for an explanation of some files.

## After the fact things
These are scripts to run after the scan to perform reconstruction, estimate the center of rotation of the reconstructions, and other analyzes.
Take a look at the [`README`](postscan/README.md) in the [postscan subfolder](postscan) for an explanation of some files.
    
## Code snippets
These are small chunks of code (like gists) to use for various useful tasks at the beamline.
Take a look at the [`README`](snippets/README.md) in the [snippets subfolder](snippets) for an explanation of some files.
