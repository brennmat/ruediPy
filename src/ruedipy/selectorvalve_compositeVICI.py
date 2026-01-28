# Code for the composite-VICI selector valve class (multiple VICI hardware valves controlled by one single software object)
# 
# DISCLAIMER:
# This file is part of ruediPy, a toolbox for operation of RUEDI mass spectrometer systems.
# 
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright 2026, Matthias Brennwald (brennmat@gmail.com)

try:
	import sys
	from .selectorvalve_VICI import selectorvalve_VICI
	from .misc	import misc
except ImportError as e:
	print (e)
	raise

class selectorvalve_compositeVICI:
	"""
	ruediPy class for control of composite VICI valves (multiple VICI valves controlled by one single software valve object).
	"""
	
	########################################################################################################
	
	
	def __init__( self , serialports , valvespostable , label = 'COMPOSITESELECTORVALVE' , labels = None , statusfilepath = None ):
		'''
		selectorvalve.__init__( self , serialports , valvespostable , label = 'COMPOSITESELECTORVALVE' )
		
		Initialize SELECTORVALVE object (VICI valve), configure serial port connection
		
		INPUT:
		serialports: tuple of device names of the serial ports, e.g. P = ( '/dev/ttyUSB3' , '/dev/ttyUSB4' )
		valvepostable: tuple listing the positions of the software-object valve with the positions of the individual hardware valves. Example: valvespostable = ( (1,1) , (1,2) , (3,2) ) defines a software-object valve with three positions and two hardware VICI valves, whose positions are as follows:
			Pos-1: VICI1 = position 1, VICI2 = position 1
			Pos-2: VICI1 = position 1, VICI2 = position 2
			Pos-3: VICI1 = position 3, VICI2 = position 2
		label (optional): label / name of the composite-SELECTORVALVE object (string). Default: label = 'SELECTORVALVE'
		labels (optional): labels / names of the individual SELECTORVALVE objects (tuple of strings). Default: label = ( 'VALVE1' , 'VALVE2' )
		statusfilepath: path where the status files for each VICI valve will be written (string), using the labels as file names
		
		OUTPUT:
		(none)
		'''

		try:

			# Label of the composite valve:
			self._label = label
			
			# Number of positions of the composite valve:
			self._num_positions = len (valvespostable)
			
			# Number of hardware valves in the composite valve:
			num_hw_valves = len (serialports)
			
			# Sanity check for valve positions
			for i in range(self._num_positions):
				if not len(valvespostable[i]) == num_hw_valves:
					raise ValueError("number of table entries for position " + str(i+1) + " does not match number of valves.")
				for j in range(num_hw_valves):
					if valvespostable[i][j] < 1:
						raise ValueError('Valve positions must not be less than 1.')
			
			# Table of hardware-valve positions:
			for i in range(self._num_positions):
				# check if table format is right
				if not ( len(valvespostable[i]) == num_hw_valves ):
					raise ValueError('The format of the valvespostable is not right.')
			self._valvespostable = valvespostable
			
			# Connect to hardware valves:
			self._hw_valves = [];
			for i in range(num_hw_valves):
				# add hardware valve:
				lbl = ''
				try:
					u = labels[i]
					if isinstance(u, str):
						lbl = u
				except:
					pass
				self._hw_valves.append(selectorvalve_VICI( serialport = serialports[i] , label = lbl , statusfilepath = statusfilepath))
				
			# Check if hardware valves support the required position values:
			for i in range(num_hw_valves):
				maxpos = 0
				for j in range(self._num_positions):
					maxpos = max( [ valvespostable[j][i] , maxpos ] )
				if self._hw_valves[i].getnumpos() < maxpos:
					raise ValueError("valve " + str(i+1) + " does not support " + str(maxpos) + " positions.")

			# Set initial position ("undefined")
			self._lastpos = -1

		# Error handling:
		except Exception as e:
			self.warning( 'Could not initialise composite selectorvalve:' + repr(e) )			
			raise e


	########################################################################################################
	

	def label(self):
		"""
		label = selectorvalve_compositeVICI.label()

		Return label / name of the SELECTORVALVE object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
########################################################################################################
	

	def getnumpos(self):
		"""
		positions = selectorvalve_compositeVICI.getnumpos()

		Return number of positions of the SELECTORVALVE object
		
		INPUT:
		(none)
		
		OUTPUT:
		positions: number of positions (int)
		"""
		
		return self._num_positions

	
########################################################################################################
	

	def warning(self,msg):
		# warn about issues related to operation of the valve
		# msg: warning message
		misc.warnmessage ('[' + self.label() + '] ' + msg)



########################################################################################################
	

	def setpos(self,val,f):
		'''
		selectorvalve_compositeVICI.setpos(val,f)

		Set valve position

		INPUT:
		val: new valve position (integer)
		f: datafile object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.

		OUTPUT:
		(none)
		'''
		
		val = int(val)
		
		
		if val > self.getnumpos():
			self.warning( 'Cannot set valve position to ' + str(val) + ': number of valve positions = ' + str(self.getnumpos()) + '. Skipping...' )
		
		if val < 1:
			self.warning( 'Cannot set valve position to ' + str(val) + '. Skipping...' )
		else:
			curpos = self.getpos()
			if not curpos == val: # check if valve is already at desired position
				# set positions of individual hardware valves:
				for i in range(len (self._hw_valves)):
					self._hw_valves[i].setpos(self._valvespostable[val-1][i],'nofile')
				self._lastpos = val
			
			# write to datafile
			if not f == 'nofile':
				f.write_valve_pos('SELECTORVALVE_COMPOSITEVICI',self.label(),val,misc.now_UNIX())


	########################################################################################################
	

	def getpos(self):
		'''
		pos = selectorvalve_compositeVICI.getpos()

		Get valve position

		INPUT:
		(none)

		OUTPUT:
		pos: valve postion (integer)
		'''

		return self._lastpos
