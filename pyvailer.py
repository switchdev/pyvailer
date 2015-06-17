#                                                             #
# [ pyvailer - FFMPEG utilities wrapper ]                     #
# [ http://github.com/switchdev/pyvailer for latest version ] #
# [ Distributed with GPLv2 License                          ] #
#                                                             #

# IMPORTS #

import os, logging, subprocess, re
from random import randrange

# SETTINGS #

PYVAILER_LOGGING = True				# Turns logging on / off

# FFMPEG COMMAND LINE CONSTANTS #

FFMPEG_ROOT = "ffmpeg "				# Root command for FFMPEG
FFMPEG_VIDPOS = "-ss %s "			# Select position within video file
FFMPEG_VID = "-i '%s' "				# Select video file
FFMPEG_STATICFRAME = "-vframes 1 "	# Fix FFMPEG output to 1 frame
FFMPEG_OVERWRITE = "-y "			# Set FFMPEG to overwrite
FFMPEG_OUTPUT = "'%s' "				# Output dir/filename
FFMPEG_QUALITY = "-crf %s "			# Output quality
FFMPEG_SIZE = "-s %s "			    # Output size

FFMPEG_DEFAULT = (FFMPEG_ROOT + FFMPEG_VIDPOS + FFMPEG_VID + 
				  FFMPEG_STATICFRAME + FFMPEG_OVERWRITE + 
				  FFMPEG_SIZE + FFMPEG_QUALITY + FFMPEG_OUTPUT) # Default thumbnail output CLI string

# PYVAILER CONSTANTS

PYVAILER_FTYPES = ['png', 'jpg', 'bmp', 'jpeg', 'gif']
				  
# PYVAILER [ Thumbnailer ]

class Thumbnailer:
	"""A class for creating and manipulating thumbnails from video files"""
	
	def __init__(self):
		self.videos = [] # A list containing video locations
		self.outputs = [] # A list of output locations/filenames
		self.output_data = [] # Filetype, quality (%), width (px), height (px) = "jpg:90:100:200"
		self.thumbs = [] # Each item (videos[0], outputs[0], output_data[0])

	def addVideo(self, video, output_folder=None, output_name=None, ftype=None, quality=None, width=None, height=None):
		"""Adds a video to the class data - validates input data"""	
		if not self._exists(video):
			return False
		
		if ftype == None:
			ftype = 'png'
		else:
			if not self._check_ftype(ftype):
				return False
		
		if output_folder == None:
			output_path = self._build_output_path(video, output_name, ftype)
		else:
			if not self._exists(output_folder):
				return False
			if output_name == None:
				output_path = output_folder + '/' + self._get_filename(video)
			else:
				output_path = output_folder + '/' + output_name
		
		if quality != None:
			if not 1 <= quality <= 100:
				if PYVAILER_LOGGING:
					logging.warning('class pyvailer.Thumbnailer : addVideo : quality must be in range 1-100')
				return False
		else:
			quality = 100
			
		if width == None:
			width = 100
			
		if height == None:
			height = 100
		
		# Add in check width and height, if applicable, later
		
		outdata = ("%s:%s:%s:%s" % (ftype, quality, width, height))
		
		self.videos.append(video)
		self.outputs.append(output_path)
		self.output_data.append(outdata)
		self.thumbs.append([self.videos[-1], self.outputs[-1], self.output_data[-1]])

	def createThumb(self, thumb):
		# Create thumbnail based on self.thumbs[thumb]
		try:
			thumbpos = self._get_thumb_pos(self.videos[thumb])
			video = self.videos[thumb]
		
			outdata = self.output_data[thumb].split(":")
			ftype = outdata[0]
			quality = outdata[1]
			size = outdata[2] + "x" + outdata[3]
		
			output = self.outputs[thumb] + "." + ftype
				
			try:
				comstring = (FFMPEG_DEFAULT % (thumbpos, video, size, quality, output))
				p = subprocess.Popen(comstring, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				out, err = p.communicate()
			except:
				if PYVAILER_LOGGING:
					logging.warning('pyvailer: FFMPEG command string failed. FFMPEG may not be installed on this system')
				return False
		except:
			if PYVAILER_LOGGING:
				logging.warning('class pyvailer.Thumbnailer : createThumb : fatal error: check video item exists')
			return False
			
	def createAllThumbs(self):
		#nothumbs = len(self.thumbs) - 1
		
		for x in range(len(self.thumbs)):
			self.createThumb(x)
			
	def listVideos(self):
		print('')
		y = 0
		for x in self.thumbs:
			outdata = x[2].split(":")
			print('No: %s' % y)
			print('Video File: %s' % x[0])
			print('Output File: %s' % x[1])
			print('Output File Type: %s' % outdata[0])
			print('Output Quality: %s CRT' % outdata[1])
			print('Output Width: %s' % outdata[2])
			print('Output Height: %s' % outdata[3])
			print('')
			y = y + 1
			
	def setAll(self, ftype=None, quality=None, width=None, height=None):
		"""Sets all videos in videolist to chosen parameters"""
		if ftype != None:
			if not self._check_ftype(ftype):
				return False
		
		if quality != None:
			if 1 <= quality <= 100:
				if PYVAILER_LOGGING:
					logging.warning('class pyvailer.Thumbnailer : setAll : quality must be between 1-100')
				return False
		
		for x in range(len(self.output_data)):
			outdata = self.output_data[x].split(":")
			
			if ftype != None:
				outdata[0] = ftype
			if quality != None:
				outdata[1] = quality
			if width != None:
				outdata[2] = str(width)
			if height != None:
				outdata[3] = str(height)
				
			self.output_data[x] = outdata[0] + ":" + outdata[1] + ":" + outdata[2] + ":" + outdata[3]
			self.thumbs[x][2] = self.output_data[x]
		
	def _get_thumb_pos(self, video, step=5):
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
		
	def _exists(self, path):
		if not os.path.exists(path):
			if PYVAILER_LOGGING:
				logging.warning('class pyvailer.Thumbnailer : _exists : path \'%s\' cannot be found' % path)
			return False
		else:
			return True
		
	def _build_output_path(self, path, filename, filetype):
		# If filename is none
		spath = path.split("/")
			
		if filename == None:
			vtitle = spath.pop()
			vtitle = vtitle.split(".")
			vtitle_t = vtitle[0]
		else:
			spath.pop()
			vtitle_t = filename
			
		output = ''
		for item in spath:
			output = output + item + "/"
		output = output + vtitle_t
		return output

	def _get_filename(self, video):
		spath = video.split("/")
		vtitle = spath.pop()
		vtitle = vtitle.split(".")
		return vtitle[0]
		
	def _check_ftype(self, ftype):
		if not ftype in PYVAILER_FTYPES:
			if PYVAILER_LOGGING:
				logging.warning('class pyvailer.Thumbnailer : _check_ftype : filetype \'%s\' is not valid' % ftype)
			return False
		else:
			return True
			
# PYVAILER [ MAIN ]

import argparse
			
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Create video thumbnail')
	parser.add_argument('video', help='video file')
	parser.add_argument('-f', type=str, help='Output image file type')
	parser.add_argument('-q', type=int, help='Output image quality')
	parser.add_argument('-height', type=int, help='Output image height (default = 100)')
	parser.add_argument('-width', type=int, help='Output image width (default = 100)')
	parser.add_argument('-name', type=str, help='Output image name')
	parser.add_argument('-fld', type=str, help='Output image folder')
	args=parser.parse_args()

	thumblist = Thumbnailer()
	thumblist.addVideo(video=args.video, quality=args.q, ftype=args.f, width=args.width, height=args.height,
					   output_name=args.name, output_folder=args.fld)

	thumblist.createThumb(0)