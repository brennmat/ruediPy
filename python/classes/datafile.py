# Code for the datafile class
# 
# DISCLAIMER:
# This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
# 
# ruediPy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ruediPy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ruediPy.  If not, see <http://www.gnu.org/licenses/>.
# 
# ruediPy: toolbox for operation of RUEDI mass spectrometer systems
# Copyright (C) 2016  Matthias Brennwald
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga

# import time
import os
from os.path 		import expanduser

from classes.misc	import misc


class datafile:

	
	########################################################################################################
	

	def __init__(self,pth):
		"""
		obj = datafile.__init__(self,pth)
		
		Initialize DATAFILE object
		
		INPUT:
		pth: directory path where datafiles are stored (string)
		
		OUTPUT:
		obj: dafafile object
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
		lab = datafile.label()
		
		Return label / name of the DATAFILE object
		
		INPUT:
		(none)
		
		OUTPUT:
		lab: label / name (string)
		"""
		
		return 'DATAFILE'

	
	########################################################################################################
	

	def warning(self,msg):
		"""
		datafile.warning(msg)
		
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
			pat = datafile.basepath()
			
			Return the base path where datafiles are stored
			
			INPUT:
			(none)
			
			OUTPUT:
			pat: datafile base path (string)
			"""
			
			return self._basepath
	
	
	########################################################################################################
		
		
	def fid(self):
		"""
		f = datafile.fid()
		
		Return the file ID / object of the current file
		
		INPUT:
		(none)
		
		OUTPUT:
		f: datafile object
		"""
		
		return self._fid
	
	
	########################################################################################################
	
	
	def name(self):
		"""
		n = datafile.name()
		
		Return the name the current file (or empty string if not datafile has been created)
		
		INPUT:
		(none)
		
		OUTPUT:
		n: ile name (string)
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
		datafile.close()
		
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
		datafile.next()
		
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

		# write header with data format info:
	   	self.writeComment(self.label(),'RUEDI data file created ' + misc.nowString() )
	   	self.writeComment(self.label(),'Data format:')
	   	self.writeComment(self.label(),'EPOCHTIME DATASOURCE[LABEL/NAME] TYPE: DATAFIELD-1; DATAFIELD-2; DATAFIELD-3; ...')
	   	self.writeComment(self.label(),'EPOCH TIME: UNIX time (seconds after Jan 01 1970 UTC), DATASOURCE: data origin (with optional label of origin object), TYPE: type of data, DATAFIELD-i: data fields, separated by colons. The field format and number of fields depends on the DATASOURCE and TYPE of data.')
	   	
	   	# write analysis type:
	   	if typ == '':
	   		typ = 'UNKNOWN'
		self.write_analysis_type( self.label() , typ , misc.nowUNIX() )

	########################################################################################################

	
	def writeln(self,caller,label,identifier,data,timestmp):
		"""
		datafile.writeln(caller,identifier,data,timestmp)
		
		Write a text line to the data file (format: TIMESTAMP CALLER[LABEL] IDENTIFIER: DATA). CALLER, LABEL, and IDENTIFIER should not contain spaces or similar white space (will be removed before writing to file). If LABEL == '' or LABEL == CALLER, the [LABEL] part is omitted.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		identifier: data type identifier (string)
		data: data / info string
		timestmp: timestamp of the data in unix time (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		# remove whitespace / spaces:
		caller 		= caller.replace(' ','')
		label 		= label.replace(' ','')
		identifier	= identifier.replace(' ','')
		
		# combine CALLER and LABEL part:
		if not (label == caller):
			if not (label == ''):
				caller = caller + '[' + label + ']'			
		
		# combine all fields:
		S = caller + ' ' + identifier + ': ' + data
		
		# make sure the string contains no newlines and line breaks:
		S = S.replace('\n', '').replace('\r', '')
				
		# format line:
		S = str(timestmp) + ' ' + S + '\n'

		# write to file:
		try:
			self.fid.write(S)	# write line to data file
			self.fid.flush()	# make sure data gets written to file now, don't wait for flushing file buffer
		except IOError, e:
			self.warning ('could not write to file ' + self.fid.name + ': ' + e)


	########################################################################################################

	
	def writeComment(self,caller,cmt):
		"""
		datafile.writeComment(caller,cmt)
		
		Write COMMENT line to the data file.
		
		INPUT:
		caller: label / name of the calling object (string)
		cmt: comment string
		
		OUTPUT:
		(none)
		"""
		
		# cmt: comment line
		self.writeln( caller, '' , 'COMMENT' , cmt , misc.nowUNIX() )
		
	
	########################################################################################################

	
	def write_analysis_type( self , caller , typ , timestmp ):
		"""
		datafile.write_analysis_type( caller , typ , timestmp )
		
		Write ANALYSIS TYPE info line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		typ: analysis type (string / char)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		typ = typ.replace(' ','');
		
		s = 'type=' + typ
		self.writeln(caller,'','ANALYSISTYPE',s,timestmp)


	########################################################################################################

	
	def writePeak(self,caller,label,mz,intensity,unit,det,gate,timestmp):
		"""
		datafile.writePeak(caller,mz,intensity,unit,det,gate,timestmp)
		
		Write PEAK data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		mz: mz value (integer)
		intensity: peak intensity value (float)
		unit: unit of peak intensity value (string)
		det: detector (string), e.g., det='F' for Faraday or det='M' for multiplier
		gate: gate time (float)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		det = det.replace(' ','');
		
		s = 'mz=' + str(mz) + ' ; intensity=' + str(intensity) + ' ' + unit + ' ; detector=' + det + ' ; gate=' + str(gate) + ' s'
		self.writeln(caller,label,'PEAK',s,timestmp)


	########################################################################################################

	
	def writeZero(self,caller,label,mz,mz_offset,intensity,unit,det,gate,timestmp):
		"""
		datafile.writeZero(caller,mz,mz_offset,intensity,unit,det,gate,timestmp)
		
		Write ZERO data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		mz: mz value (integer)
		mz_offset: mz offset value (integer, positive offset corresponds to higher mz value)
		intensity: zero intensity value (float)
		unit: unit of peak intensity value (string)
		det: detector (string), e.g., det='F' for Faraday or det='M' for multiplier
		gate: gate time (float)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		det = det.replace(' ','');
		if mz_offset > 0:
			offset = '+'+str(mz_offset)
		else:
			offset = str(mz_offset)
		
		s = 'mz=' + str(mz) + ' ; mz-offset=' + offset + ' ; intensity=' + str(intensity) + ' ' + unit + ' ; detector=' + det + ' ; gate=' + str(gate) + ' s'
		self.writeln(caller,label,'ZERO',s,timestmp)


	########################################################################################################

	
	def writeScan(self,caller,label,mz,intensity,unit,det,gate,timestmp):
		"""
		datafile.writeScan(caller,mz,intensity,unit,det,gate,timestmp)
		
		Write PEAK data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		mz: mz values (floats)
		intensity: intensity values (floats)
		unit: unit of intensity values (string)
		det: detector (string), e.g., det='F' for Faraday or det='M' for multiplier
		gate: gate time (float)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		s = 'mz=' + str(mz) + ' ; intensity=' + str(intensity) + ' ' + unit + '; detector=' + det + ' ; gate=' + str(gate) + ' s'
		self.writeln(caller,label,'SCAN',s,timestmp)


	########################################################################################################

	
	def writeValvePos(self,caller,label,position,timestmp):
		"""
		datafile.writeValvePos(caller,position,timestmp)
		
		Write multi-port valve position data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		position: valve position (integer)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
		
		s = 'position=' + str(position)
		self.writeln(caller,label,'POSITION',s,timestmp)


	########################################################################################################

	
	def write_pressure(self,caller,label,value,unit,timestmp):
		"""
		datafile.write_pressure(caller,label,value,unit,timestmp)
				
		Write PRESSURE data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		value: pressure value (float)
		unit: unit of peak intensity value (string)
		timestmp: timestamp of the peak measurement (see misc.nowUNIX)
		
		OUTPUT:
		(none)
		"""
				
		s = 'pressure=' + str(value) + ' ' + unit
		self.writeln(caller,label,'PRESSURE',s,timestmp)
