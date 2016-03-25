# Code for the datafile class

# import time
import os
from os.path 		import expanduser

from classes.misc	import misc


class datafile:

	
	########################################################################################################
	

	def __init__(self,pth):
		# Initialize datafile object
		# pth: directory path where datafiles are stored (string)
		
		# remove trailing whitespace (just in case):
		pth = pth.strip()
		
		# check for tilde in pth (as shortcut for home directory), and replace with full path
		if pth[0] == '~':
			pth = pth.replace("~", expanduser("~"))
				
		# check if path exists and is accessible for writing:		
		if not os.access(pth, os.W_OK):
			misc.warnmessage ('DATAFILE','path \'' + pth + '\' is not accessible for writing!')
		
		# remember base path:
		self._basepath = pth
		
		# init empty file ID:
		self._fid = -1

	
	########################################################################################################
	

	def warning(self,msg):
		# warn about issues related to DATAFILE object
		# msg: warning message
		misc.warnmessage ('DATAFILE',msg)
	
	
	########################################################################################################
	
	
	def basepath(self):
			# return the base path where datafile are stored
			return self._basepath
	
	
	########################################################################################################
		
		
	def fid(self):
		# return the file ID / object of the current file
		return self._fid
	
	
	########################################################################################################
	
	
	def name(self):
		# return the name the current file (or empty string if not datafile has been created)
		
		# check if file / fid has been created as a file object:
		if hasattr(self.fid, 'name'):
			# return the file name
			return self.fid.name
		else:
			return ''
	
	
	########################################################################################################
	
	
	def close(self):
		# check if file / fid has been created as a file object:
		if hasattr(self.fid, 'close'):
			# close current data file
			try:
				self.fid.close()
			except IOError, e:
				self.warning ('could not close file ' + self.fid.name() + ': ' + e)
	
	
	########################################################################################################

		
	def next(self,typ=''):
		# close current data file (if it's still open) and start a new file
		# typ (optional): string that will be appended to the file name (useful to indicate 'type' of mesurement data, e.g. typ = 'SAMPLE', typ = 'S', typ = 'BLANK', typ = 'B', typ = 'CAL', typ = 'C', etc.). The string can be anything. If omitted or typ = '', nothing will be appended to the file name

		# close the current datafile (if it exists and is still open)
		self.close()
		
		# determine file name for new file
		n = misc.nowString()
		n = n.replace(':','-')
		n = n.replace(' ','_')
		if not ( typ == '' ):
			n = n + '_' + typ
		
		# check if file exists already:
		n0 = self.basepath() + os.sep + n
		n = n0
		k = 1
		while os.path.isfile(n + '.txt'):
			n = n0 + '+' + str(k)
			k = k+1
		
		# open the file
		n = n + '.txt'
		try:
			self.fid = open(n, 'w')
			    		
		except IOError, e:
			self.fid = -1;
			self.warning ('could not open new file (' + n + '): ' + str(e))
			return # exit

	   	self.writeComment('RUEDI data file created ' + misc.nowString() )
		self.writeComment('First column: UNIX epoch time (seconds after Jan 01 1970 UTC)')
		self.writeComment('Second column: data type identifier')


	########################################################################################################

	
	def writeln(self,identifier,data,timestmp = misc.nowUNIX()):
		# write a text line to the data file. The line starts with the timestamp, followed by the string.
		# identifier: data type identifier (string)
		# data: data / info string
		# timestmp: timestamp of the data line in unix time / epoch format (seconds after Jan 01 1970 UTC)
		
		S = identifier + ': ' + data
		
		# make sure the string contains no newlines and line breaks:
		S = S.replace('\n', '').replace('\r', '')
				
		# format line:
		S = str(timestmp) + ' ' + S + '\n'
		
		# write to file:
		try:
			self.fid.write(S)
		except IOError, e:
			self.warning ('could not write to file ' + self.fid.name + ': ' + e)


	########################################################################################################

	
	def writeComment(self,cmt):
		# write COMMENT line to the data file.
		# cmt: comment line
		self.writeln( 'COMMENT' , cmt , misc.nowUNIX() )
		
	
	########################################################################################################

	
	def writePeak(self,mz,peak,unit,gate,timestmp):
		# write PEAK data line to the data file.
		# mz: mz value
		# peak: peak value
		# unit: unit of peak value (string)
		# timestmp: timestamp of the peak measurement (see datafile.writeln)
		
		s = 'mz=' + str(mz) + ', value=' + str(peak) + ' ' + unit + ', gate=' + str(gate) + ' s'
		self.writeln('PEAK',s,timestmp)