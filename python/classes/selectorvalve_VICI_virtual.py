# Code for virtual VICI selector valve class (mostly useful for development or demo purposes without acces to a real VICI valve)
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
# Copyright 2020, Matthias Brennwald (brennmat@gmail.com)

try:
	import sys
	import warnings
	import serial
	import time
	from classes.misc	import misc
	from classes.selectorvalve_VICI import selectorvalve_VICI
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
		
		Initialize SELECTORVALVE object (virutal VICI valve)
		
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
				f.write_valve_pos('SELECTORVALVE_VICI_VIRTUAL',self.label(),val,misc.now_UNIX())

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
