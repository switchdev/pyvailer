# PyVailer - Python Based Video Thumbnailer
# Tested on Linux/Lubuntu 64 Bit, Python 3x - requires FFMPEG to be installed
# on the system to work

# CreateThumb function creates a thumbnail based on a randomly
# picked timeframe within the video

import subprocess
from random import randrange
import os, logging, re

# SETTINGS

PYVAILER_LOGGING = True				# Turns logging on / off
PYVAILER_CONFIRM = True				# Turns on console output in testing (__main__)

# FFMPEG CONSTANTS

FFMPEG_ROOT = "ffmpeg "				# Root command for FFMPEG
FFMPEG_VIDPOS = "-ss %s "			# Select position within video file
FFMPEG_VID = "-i '%s' "				# Select video file
FFMPEG_STATICFRAME = "-vframes 1 "	# Fix thumb to one image
FFMPEG_OVERWRITE = "-y "			# Set FFMPEG to overwrite
FFMPEG_OUTPUT = "'%s' "				# Output dir/filename
FFMPEG_DEFAULT = FFMPEG_ROOT + FFMPEG_VIDPOS + FFMPEG_VID + FFMPEG_STATICFRAME + FFMPEG_OVERWRITE + FFMPEG_OUTPUT

def CreateThumb(video):
	""" Function that creates an image from a randomly picked frame from a
		specified video file."""
		
	# Check that the video exists/is readable
	if not os.path.exists(video):
		if PYVAILER_LOGGING:
			logging.warning('%s does not exist, or cannot be accessed', video)
		return False
	
	# break down video location/filename
	spath = video.split("/")
	vtitle = spath.pop()
	vtitle = vtitle.split(".")
	vtitle_noex = vtitle[0]
		
	# rebuild with .png extention
	output = ''
	for item in spath:
		output = output + item + "/"
	output = output + vtitle_noex + ".png"
			
	# Set thumbnail position
	thumbpos = GetThumbPos(video)
	
	# Build FFMPEG string & execute
	try:
		comstring = (FFMPEG_DEFAULT % (thumbpos, video, output))
		p = subprocess.Popen(comstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		out, err = p.communicate()
	except:
		if PYVAILER_LOGGING:
			logging.warning('FFMPEG command string failed. FFMPEG may not be installed on this system')
		return False
	
	# Code executed without issue: assume thumbnail generation succeeded
	# Ensure thumb exists
	if ThumbExists(video):
		return True
	else:
		return False
	
	# something went wrong
	return False

def GetThumbPos(video, step=5):
	"""Function for determining a valid position, in seconds, within a video that a valid
	   thumbnail can be created from. Returns an integer."""
	
	if not os.path.exists(video): # Check that video exists
		if PYVAILER_LOGGING:
			logging.warning('%s does not exist or cannot be accessed', video)
		return None
	
	COMMSTRING = ("ffmpeg -i '%s'" % video)

	process = subprocess.Popen([COMMSTRING], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
	stdout = str(process.communicate())
	matches = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", stdout, re.DOTALL).groupdict()
 
	h = int(matches['hours'])
	m = int(matches['minutes'])
	s_t = matches['seconds']
	s = int(s_t[:2])

	video_duration = 3600*h + 60*m + s
	
	randpos = randrange(0, int(video_duration), step) # Generate a random position in the video
	m, s = divmod(randpos, 60)
	h, m = divmod(m, 60)
	pos = "%02d:%02d:%02d.000" % (h, m, s)
	return pos

def ThumbExists(video):
	""" Function that checks to see if an image file exists that matches
		a video's filename string, excluding file extension."""
		
	spath = video.split("/")
	vtitle = spath.pop()
		
	vtitle = vtitle.split(".")
	vtitle_noex = vtitle[0]
		
	# rebuild with .png extention
	output = ''
	for item in spath:
		output = output + item + "/"
	output = output + vtitle_noex + ".png"
	
	if os.path.exists(output):
		return True
	else:
		return False

# STANDALONE EXECUTION / TESTING

import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create video thumbnail')
	parser.add_argument('video', help='video file')
	
	args=parser.parse_args()
	
	pyvailer_exe = CreateThumb(args.video)
	
	if PYVAILER_CONFIRM:
		if pyvailer_exe:
			print('PyVailer ran with no errors')
		else:
			print('PyVailer failed to run correctly')
