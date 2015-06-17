# pyvailer
pyvailer is a Python based video thumbnail generator. Basically, it's a very simple (so far) Python module that takes a video and generates an image based off a randomly selected frame. At this time, pyvailer is simply wrapping existing FFMPEG commands in a convenient and reusable format. Obviously, this means that in order for pyvailer to function you'll need FFMPEG installed.

## Installation

FFMPEG is required for pyvailer to work. For pyvailer itself, either download the pyvailer.py file to your harddrive or clone the git repository. Just import pyvailer into your own program and call the functions you need.

**Note: pyvailer has only been tested on Linux/Ubuntu (64 Bit) and Python 3x. It shouldn't be too much work to get it working with Python 2x. I have no idea if it works on Windows yet. I'll try and get a Python 2x version available, as well as get cross-platform compatibility done.**

## Using pyvailer

### As a standalone program

Copy the pyvailer.py file somewhere on your harddrive. From the command line, invoke the script in python and append a video file, including the whole path. For example, on Ubuntu:

`python pyvailer.py ~/Videos/myvideo.mp4`

This will generate a `myvideo.png` image file within the same folder in which the video file is located.

### As a module

Copy the pyvailer.py into the same folder as your project's script (you *can* go through the hassle of manually installer pyvailer the proper way, so that Python will always find it, but while it remains a single-source module I'm not going to provide this as standard). Import it as you would any other module. A list of available functions below.

## Functionality

*What does pyvailer actually do?*

###pyvailer.CreateThumb(*video*)

This function creates a thumbnail image for a video (will full path) passed to it. Returns false if something goes wrong (note: do not rely on this, not fully implemented). Will always overwrite existing thumbnail.

###pyvailer.GetThumbPos(*video*, *step=5*)

This function returns a string - to a time format that FFMPEG understands - containing a random time position within a passed video file. Used for determining a random frame from which to create a thumbnail from. Returns as:

`HH:MM:SS.000`

The *step* variable is for minimum amounts between integers returned by the random number generator. It would be beneficial to set a low step number for short video files (1-2) and larger numbers for longer video files (to save on resources used to generate random number).

###pyvailer.ThumbExists(*video*)

Checks to see if a thumbnail exists for a provided video file. For example, passing the following to the *video* variable:

`/home/user/video.mp4`

checks to see if

`/home/user/video.png'

exists, and if so returns True.

(check commit)
