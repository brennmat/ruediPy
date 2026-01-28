# Code for virtual VICI selector valve class (mostly useful for development or demo purposes without acces to a real VICI valve)
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
	import warnings
	import serial
	import time
	from .misc	import misc
	from .selectorvalve_VICI import selectorvalve_VICI
except ImportError as e:
	print (e)
	raise

class selectorvalve_VICI_virtual(selectorvalve_VICI):
	"""
	ruediPy class for virtual VICI valve.
	"""
	
	########################################################################################################
	
	
	def __init__( self , serialport=None , label = 'SELECTORVALVE', numpos = 6 ):
		'''
		selectorvalve_VICI_virtual.__init__( serialport = None, label = 'SELECTORVALVE', numpos = 6 )
		
		Initialize SELECTORVALVE object (virtual VICI valve)
		
		INPUT:
		serialport (optional): device name of the serial port, e.g. P = '/fake/serialport/to/virtual/valve'
		label (optional): label / name of the SELECTORVALVE object (string). Default: label = 'SELECTORVALVE'
		numpos (optional): number of valve positions (default: 6)
		
		OUTPUT:
		(none)
		'''

		try:
			if type(numpos) is not int:
				raise RuntimeError('Number of selector valve positions is of type ' + str(type(numpos)) + ', but must an integer.')				
			if numpos < 1:
				raise RuntimeError('Number of selector valve positions is ' + str(numpos) + ', but must be > 0.')
		except Exception as e:
			raise e
		
		self._serialport = serialport;
		self._label = label
		self._num_positions = numpos
		self._position = -1
						
		self.log ( 'Successfully configured virtual VICI selector valve on ' + serialport + ', number of positions = ' + str(self._num_positions) )

	
########################################################################################################
	

	def set_legacy(self):
		'''
		selectorvalve_VICI_virtual.set_legacy()

		Set communication protocol to LEGACY mode (does nothing with virtual valve).

		INPUT:
		(none)

		OUTPUT:
		(none)
		'''
		
		time.sleep(0.5)


	########################################################################################################
	

	def setpos(self,val,f):
		'''
		selectorvalve_VICI_virtual.setpos(val,f)

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
				# send command to serial port:
				self._position = val
			
			# write to datafile
			if not f == 'nofile':
				f.write_valve_pos('SELECTORVALVE_VICI',self.label(),val,misc.now_UNIX())

			# give the valve some time to actually do the switch:
			time.sleep(0.5)


	########################################################################################################
	

	def getpos(self):
		'''
		pos = selectorvalve_VICI_virtual.getpos()

		Get valve position

		INPUT:
		(none)

		OUTPUT:
		pos: valve postion (integer)
		'''

		return self._position
