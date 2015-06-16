# PyVailer - Python Based Video Thumbnailer
# Tested on Linux/Lubuntu 64 Bit, Python 3x - requires FFMPEG to be installed
# on the system to work

# CreateThumb function creates a thumbnail based on a randomly
# picked timeframe within the video

import subprocess
from random import randrange
import os, logging

def CreateThumb(video):
	""" Function that creates an image from a randomly picked frame from a
		specified video file."""
		
	# Check that the video exists/is readable
	if not os.path.exists(video):
		logging.WARNING('%s does not exist, or cannot be accessed', video)
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
		comstring = ("ffmpeg -ss %s "
							  "-i '%s' "
							  "-vframes 1 -y "
							  "'%s'" % (thumbpos, video, output))

		# Execute string in shell
		subprocess.check_output(comstring, shell=True)
	except:
		logging.WARNING('FFMPEG command string failed. FFMPEG may not be installed on this system')
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
		logging.WARNING('%s does not exist or cannot be accessed', video)
		return None
	
	commstring = ("ffmpeg -i '%s' 2>&1 "
				  "| grep \"Duration\"| cut -d ' ' -f 4 | "
				  "sed s/,// | sed 's@\..*@@g' | "
				  "awk '{ split($1, A, \":\"); split(A[3], B, \".\");"
				  " print 3600*A[1] + 60*A[2] + B[1] }'" % video)
				  
	try:	  
		with subprocess.Popen([commstring], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True) as proc:
			video_duration = proc.stdout.read()
	except:
		logging.WARNING('Video duration could not be determined')
	
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
		
# STANDALONE & TESTING

import argparse

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create video thumbnail')
	parser.add_argument('video', help='video file')
	
	args=parser.parse_args()
	
	CreateThumb(args.video)
