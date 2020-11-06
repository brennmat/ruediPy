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
# Copyright 2016, 2017, Matthias Brennwald (brennmat@gmail.com)
try:
	import sys
	import warnings
	import os
	from os.path		import expanduser

	from classes.misc	import misc
except ImportError as e:
	print (e)
	raise

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / rams_SRS class is running on Python version < 3. Version 3.0 or newer is recommended!")

class datafile:
	"""
	ruediPy class for handling of data files.
	"""
	
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
			self.warning ('path \'' + pth + '\' is not accessible for writing!')
		
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
		
		misc.warnmessage (msg)
	
	
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
			except IOError as e:
				self.warning ('could not close file ' + self.fid.name() + ': ' + e)
	
	
	########################################################################################################

		
	def next( self , typ='' , samplename='' , standardconc=[] ):
		"""
		datafile.next( typ='MISC' , samplename='' , standardconc=[] )
				
		Close then current data file (if it's still open) and start a new file.
		
		INPUT:
		typ (optional): analysis type (string, default: typ = 'MISC'). The analysis type is written to the data file, and is appended to the file name. typ can be one of the following analysis types:
			typ = 'SAMPLE' (for sample analyses)
			typ = 'STANDARD' (for standard / calibration analyses)
			typ = 'BLANK' (for blank analyses)
			typ = 'MISC' (for miscellaneous analysis types, useful for testing, maintenance, or similar purposes)
		samplename (optional, only used if typ='SAMPLE'): description, name, or ID of sample (string)
		standardconc (optional, only used if typ='STANDARD'): standard gas information, list of 3-tuples, one tuple for each mz-value). Each tuple has the following 3 fields:
			field-1: name of species (string)
			field-2: volumetric species concentration in standard gas
			field-3: mz value used for analysis of this species
			
			example for N2 and Ar-40 in air, analyzed on mz=28 and mz=40: standardconc = [ ('N2',0.781,28) , ('Ar-40',0.9303,40) ]
					
		OUTPUT:
		(none)
		"""

		# close the current datafile (if it exists and is still open)
		self.close()
		
		# parse analysis type:
		typ = typ.replace(' ','')
		typ = typ.upper()
		if not ( typ == '' ):
			if not ( typ in ( 'SAMPLE' , 'STANDARD' , 'BLANK' , 'MISC' ) ):
				self.warning ( 'Unknown analysis type ' + typ + '. Ignoring analysis type...' )
				typ = ''
		
		# determine file name for new file
		n = misc.now_string()
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

		except IOError as e:
			self.fid = -1;
			self.warning ('could not open new file (' + n + '): ' + str(e))
			return # exit

		# write header with data format info:
		self.write_comment(self.label(),'RUEDI data file created ' + misc.now_string() )
		self.write_comment(self.label(),'Data format:')
		self.write_comment(self.label(),'EPOCHTIME DATASOURCE[LABEL/NAME] TYPE: DATAFIELD-1; DATAFIELD-2; DATAFIELD-3; ...')
		self.write_comment(self.label(),'EPOCH TIME: UNIX time (seconds after Jan 01 1970 UTC), DATASOURCE: data origin (with optional label of origin object), TYPE: type of data, DATAFIELD-i: data fields, separated by colons. The field format and number of fields depends on the DATASOURCE and TYPE of data.')

		# write analysis type:
		if typ == '':
			typ = 'UNKNOWN'
		self.writeln( self.label() ,'','ANALYSISTYPE' , typ , misc.now_UNIX() )
		
		# write sample name:
		if typ == 'SAMPLE':
			if samplename == '':
				self.warning('No sample name given!')
			else:
				self.writeln( self.label() ,'','SAMPLENAME' , samplename , misc.now_UNIX() )

		# write standard gas information:
		if typ == 'STANDARD':
			if len(standardconc) == 0:
				self.warning('Standard gas information missing!')
			else:
				for i in range(0,len(standardconc)):
					self.write_standard_conc(standardconc[i][0],standardconc[i][1],standardconc[i][2])



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
		timestmp: timestamp of the data in unix time (see misc.now_UNIX)
		
		OUTPUT:
		(none)
		"""
		
		# remove whitespace / spaces:
		caller     = caller.replace(' ','')
		label      = label.replace(' ','')
		identifier = identifier.replace(' ','')
		
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
		except IOError as e:
			self.warning ('could not write to file ' + self.fid.name + ': ' + e)


	########################################################################################################

	
	def write_comment(self,cmt,caller=None):
		"""
		datafile.write_comment(cmt,caller=None)
		
		Write COMMENT line to the data file.
		
		INPUT:
		cmt: comment string
		caller (deprecated!): caller label / name of the calling object (string). The 'caller' argument is depracated and is determined automatically.
		
		OUTPUT:
		(none)
		"""
		
		if caller is not None:
			# old-style (depracated!) way of write_comment call!
			# write_comment( caller, cmt )
			print( 'Calling datafile.write_comment(...) with TWO arguments is deprecated!' , file=sys.stderr )
			print('   cmt = ' + caller , file=sys.stderr )
			print('   caller (ignored!) = ' + cmt , file=sys.stderr )
			cmt = caller
	
		caller_frame = inspect.stack()[1]
		caller_filename = caller_frame.filename
		caller = os.path.splitext(os.path.basename(caller_filename))[0]

		M = caller + ' at ' + misc.now_string() + ': ' + cmt
		
		# cmt: comment line
		self.writeln( caller, '' , 'COMMENT' , cmt , misc.now_UNIX() )
		
	
	########################################################################################################


	def write_standard_conc(self,species,conc,mz):
		"""
		datafile.write_standard_conc(species,conc,mz)
		
		Write line with standard/calibration gas information to data file: name, concentration/mixing ratio, and mz value of gas species.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		species: name of gas species (string)
		conc: volumetric concentration / mixing ratio (float)
		mz: mz value (integer)
		
		OUTPUT:
		(none)
		"""
		
		s = 'species=' + species + ' ; concentration=' + str(conc) + ' vol/vol ; mz=' + str(mz)
		self.writeln(self.label(),'','STANDARD',s,misc.now_UNIX())


	########################################################################################################


	def write_sample_desc(self,desc):
		"""
		datafile.write_sample_desc(self,desc)
		
		Write line with sample description (e.g., name or ID of sample)
		
		INPUT:
		desc: sample description, name, or ID (string)
		
		OUTPUT:
		(none)
		"""
		
		self.writeln(self.label(),'','SAMPLENAME',desc,misc.now_UNIX())


	########################################################################################################

	
	def write_peak(self,caller,label,mz,intensity,unit,det,gate,timestmp,peaktype=None):
		"""
		datafile.write_peak(caller,mz,intensity,unit,det,gate,timestmp,peaktype=None)
		
		Write PEAK data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		mz: mz value (integer)
		intensity: peak intensity value (float)
		unit: unit of peak intensity value (string)
		det: detector (string), e.g., det='F' for Faraday or det='M' for multiplier
		gate: gate time (float)
		timestmp: timestamp of the peak measurement (see misc.now_UNIX)
		peaktype (optional): string to indicate the "type" of the PEAK reading (default: type=None). Specifying type will add the type string the the PEAK identifier in the data file in order to tell the processing tool(s) to use the PEAK_xyz reading for a specific purpose. Example: type='DECONV' will change the PEAK identifier to PEAK_DECONV, which will be used for deconvolution of mass spectrometric overlaps.
		
		OUTPUT:
		(none)
		"""
		
		det = det.replace(' ','');
		
		s = 'mz=' + str(mz) + ' ; intensity=' + str(intensity) + ' ' + unit + ' ; detector=' + det.upper() + ' ; gate=' + str(gate) + ' s'
		if peaktype:
			p = 'PEAK_' + peaktype.upper()
		else:
			p = 'PEAK'

		self.writeln(caller,label,p,s,timestmp)


	########################################################################################################

	
	def write_zero(self,caller,label,mz,mz_offset,intensity,unit,det,gate,timestmp,zerotype=None):
		"""
		datafile.write_zero(caller,mz,mz_offset,intensity,unit,det,gate,timestmp,zerotype=None)
		
		Write ZERO data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		mz: mz value (integer)
		mz_offset: mz offset value (integer, positive offset corresponds to higher mz value)
		intensity: zero intensity value (float)
		unit: unit of zero intensity value (string)
		det: detector (string), e.g., det='F' for Faraday or det='M' for multiplier
		gate: gate time (float)
		timestmp: timestamp of the zero measurement (see misc.now_UNIX)
		zerotype (optional): string to indicate the "type" of the ZERO reading (default: type=None). Specifying type will add the type string the the ZERO identifier in the data file in order to tell the processing tool(s) to use the ZERO_xyz reading for a specific purpose. Example: type='DECONV' will change the ZERO identifier to ZERO_DECONV, which will be used for deconvolution of mass spectrometric overlaps.
		
		OUTPUT:
		(none)
		"""
		
		det = det.replace(' ','');
		if mz_offset > 0:
			offset = '+'+str(mz_offset)
		else:
			offset = str(mz_offset)
		if zerotype:
			p = 'ZERO_' + zerotype.upper()
		else:
			p = 'ZERO'

		s = 'mz=' + str(mz) + ' ; mz-offset=' + offset + ' ; intensity=' + str(intensity) + ' ' + unit + ' ; detector=' + det.upper() + ' ; gate=' + str(gate) + ' s'
		self.writeln(caller,label,p,s,timestmp)


	########################################################################################################

	
	def write_scan(self,caller,label,mz,intensity,unit,det,gate,timestmp):
		"""
		datafile.write_scan(caller,mz,intensity,unit,det,gate,timestmp)
		
		Write PEAK data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		mz: mz values (floats)
		intensity: intensity values (floats)
		unit: unit of intensity values (string)
		det: detector (string), e.g., det='F' for Faraday or det='M' for multiplier
		gate: gate time (float)
		timestmp: timestamp of the peak measurement (see misc.now_UNIX)
		
		OUTPUT:
		(none)
		"""
		
		s = 'mz=' + str(mz) + ' ; intensity=' + str(intensity) + ' ' + unit + '; detector=' + det + ' ; gate=' + str(gate) + ' s'
		self.writeln(caller,label,'SCAN',s,timestmp)


	########################################################################################################


	def write_ms_deconv(self,caller,label,target_mz,target_species,deconv_detector,ms_EE,basis,timestmp):
		"""
		datafile.write_ms_deconv(caller,label,target_mz,target_species,deconv_detector,ms_EE,basis,timestmp)
		
		Write DECONVOLUTION line to the data file (information for deconvolution processor).
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		target_mz: m/z ratio of the peak that needs "overlap correction by deconvolution" (integer)
		target_species: name of the gas species that needs "overlap correction by deconvolution" (string)
		deconv_detector: indicates whether deconvolution (regression of linear model) is based on Faraday or Multiplier data (string, either 'F' or 'M')
		ms_EE: ionisation energy used for the analysis in the MS ion source (float, in eV)
		basis: spectra (or "endmembers") to be used as basis for deconvolution (Pyhton tuple). Every tuple element is of the form ('speciesname',mz1,peakheight1,mz2,peakheight2,...,mzN,peakheightN). Example: basis=( ('CH4',13,0.12,14,0.205,15,0.902,16,1.0) , ('N2',14,0.13,15,0.00043,28,1.0,29,0.0035) , ('O2',16,0.21,32,1.0) )

		gate: gate time (float)
		timestmp: timestamp of the peak measurement (see misc.now_UNIX)
		
		OUTPUT:
		(none)
		"""
		
		s = 'target_mz=' + str(target_mz) + ' ; target_species=' + target_species + ' ; detector = ' + deconv_detector.upper() + ' ; MS_EE=' + str(ms_EE) + ' eV ; basis=' + str(basis)
		self.writeln(caller,label,'DECONVOLUTION',s,timestmp)


	########################################################################################################

	
	def write_valve_pos(self,caller,label,position,timestmp):
		"""
		datafile.write_valve_pos(caller,position,timestmp)
		
		Write multi-port valve position data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		position: valve position (integer)
		timestmp: timestamp of the peak measurement (see misc.now_UNIX)
		
		OUTPUT:
		(none)
		"""
		
		# s = 'position=' + str(position)
		s = str(position)
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
		timestmp: timestamp of the pressure measurement (see misc.now_UNIX)
		
		OUTPUT:
		(none)
		"""
				
		s = str(value) + ' ' + unit
		self.writeln(caller,label,'PRESSURE',s,timestmp)


	########################################################################################################

	
	def write_temperature(self,caller,label,value,unit,timestmp):
		"""
		datafile.write_temperature(caller,label,value,unit,timestmp)
				
		Write TEMPERATURE data line to the data file.
		
		INPUT:
		caller: type of calling object, i.e. the "data origin" (string)
		label: name/label of the calling object (string)
		value: temperature value (float)
		unit: unit of peak intensity value (string)
		timestmp: timestamp of the temperature measurement (see misc.now_UNIX)
		
		OUTPUT:
		(none)
		"""
				
		s = str(value) + ' ' + unit
		self.writeln(caller,label,'TEMPERATURE',s,timestmp)
