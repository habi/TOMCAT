# Pre-scan scripts
These scripts are meant to be run before a scan is started and are used for alignment.

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
