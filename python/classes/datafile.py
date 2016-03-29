# Code for the datafile class

# import time
import os
from os.path 		import expanduser

from classes.misc	import misc


class datafile:

	
	########################################################################################################
	

	def __init__(self,pth):
		"""
		Initialize DATAFILE object
		
		INPUT:
		pth: directory path where datafiles are stored (string)
		
		OUTPUT:
		dafafile object
		"""
		
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
	

	def label(self):
		"""
		Return label / name of the DATAFILE object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return 'DATAFILE'

	
	########################################################################################################
	

	def warning(self,msg):
		"""
		Warn about issues related to DATAFILE object
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		"""
		
		misc.warnmessage ('DATAFILE',msg)
	
	
	########################################################################################################
	
	
	def basepath(self):
			"""
			Return the base path where datafiles are stored
			
			INPUT:
			(none)
			
			OUTPUT:
			Datafile base path (string)
			"""
			
			return self._basepath
	
	
	########################################################################################################
		
		
	def fid(self):
		"""
		Return the file ID / object of the current file
		
		INPUT:
		(none)
		
		OUTPUT:
		File object
		"""
		
		return self._fid
	
	
	########################################################################################################
	
	
	def name(self):
		"""
		Return the name the current file (or empty string if not datafile has been created)
		
		INPUT:
		(none)
		
		OUTPUT:
		File name (string)
		"""
		
		# check if file / fid has been created as a file object:
		if hasattr(self.fid, 'name'):
			# return the file name
			return self.fid.name
		else:
			return ''
	
	
	########################################################################################################
	
	
	def close(self):
		"""
		Close the currently open data file (if any)
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		"""
		
		#Check if file / fid has been created as a file object:
		if hasattr(self.fid, 'close'):
			# close current data file
			try:
				self.fid.close()
			except IOError, e:
				self.warning ('could not close file ' + self.fid.name() + ': ' + e)
	
	
	########################################################################################################

		
	def next(self,typ=''):
		"""
		Close then current data file (if it's still open) and start a new file.
		
		INPUT:
		typ (optional): string that will be appended to the file name. This may be useful to indicate 'type' of mesurement data, e.g. typ = 'SAMPLE', typ = 'S', typ = 'BLANK', typ = 'B', typ = 'CAL', typ = 'C', etc.). The string can be anything. If omitted or typ = '', nothing will be appended to the file name
		
		OUTPUT:
		(none)
		"""

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
		self.writeComment('Column-1: UNIX epoch time (seconds after Jan 01 1970 UTC)')
		self.writeComment('Column-2: data type identifier')
		self.writeComment('Column-3: data or information (format depends to data type)')


	########################################################################################################

	
	def writeln(self,caller,identifier,data,timestmp):
		"""
		Write a text line to the data file (format: TIMESTAMP CALLER: IDENTIFIER DATA)
		
		INPUT:
		caller: name/label of calling object, i.e. the "data origin" (string)
		identifier: data type identifier (string)
		data: data / info string
		timestmp: timestamp of the data in unix time (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		S = caller + ': ' + identifier + ' ' + data
		
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
		"""
		Write COMMENT line to the data file.
		
		INPUT:
		cmt: comment string
		
		OUTPUT:
		(none)
		"""
		
		# cmt: comment line
		self.writeln( self.label(), 'COMMENT' , cmt , misc.nowUNIX() )
		
	
	########################################################################################################

	
	def writePeak(self,caller,mz,intensity,unit,gate,timestmp):
		"""
		Write PEAK data line to the data file.
		
		INPUT:
		caller: caller label / name (string)
		mz: mz value (integer)
		intensity: peak intensity value (float)
		unit: unit of peak intensity value (string)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		s = 'mz=' + str(mz) + ' ; intensity=' + str(intensity) + ' ' + unit + ' ; gate=' + str(gate) + ' s'
		self.writeln(caller, 'PEAK',s,timestmp)


	########################################################################################################

	
	def writeValvePos(self,caller,position,timestmp):
		"""
		Write multi-port valve position data line to the data file.
		
		INPUT:
		caller: caller label / name (string)
		position: valve position (integer)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		s = 'position=' + str(position)
		self.writeln(caller, 'NEWPOSITION',s,timestmp)
