# Code for the WIKA pressure sensor class
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

import serial
import time
from classes.misc	import misc

class pressuresensor_WIKA:

	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'PRESSURESENSOR' ):
		'''
		pressuresensor_WIKA.__init__( serialport , label = 'SELECTORVALVE' )
		
		Initialize PRESSURESENSOR object (WIKA), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. P = '/dev/ttyUSB3'
		label (optional): label / name of the PRESSURESENSOR object (string). Default: label = 'PRESSURESENSOR'
		
		OUTPUT:
		(none)
		'''
	
		# open and configure serial port for communication with VICI valve (9600 baud, 8 data bits, no parity, 1 stop bit
		ser = serial.Serial(
			port     = serialport,
			baudrate = 9600,
			parity   = serial.PARITY_NONE,
			stopbits = serial.STOPBITS_ONE,
			bytesize = serial.EIGHTBITS,
			timeout  = 5.0
		)
		ser.flushInput() 	# make sure input is empty
		ser.flushOutput() 	# make sure output is empty
		
		self.ser = ser;

		self._label = label

		# configure pressure sensor for single pressure readings on request ("polling mode")
		...

	
	########################################################################################################
	

	def label(self):
		"""
		Return label / name of the PRESSURESENSOR object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
	

	def warning(self,msg):
		# warn about issues related to operation of the pressure sensor
		# msg: warning message
		misc.warnmessage ('WIKA PRESSURE SENSOR',msg)

	
	########################################################################################################
		

	def read_pressure(self):
		# read current pressure value (in hPa)
		
		# make sure serial port buffer is empty:
		self.ser.flushInput() 	# make sure input is empty
		self.ser.flushOutput() 	# make sure output is empty

		# send command to serial port:
		self.ser.write('...')
		
		# read answer
		while self.ser.inWaiting() > 0: # while there's something in the buffer...
				ans = ans + self.ser.read() # read each byte

	    	### ans = ans.split('=')[1] # split answer in the form 'Position is  = 1'
	    	### ans = ans.strip() # strip away whitespace
	    	
	    	# check result:
		if not ans.isdigit():
			self.warning('could not determine pressure value (pressure = ' + ans + ')')
			ans = '-1'
		
		# convert value to hPa:
		ans = ans * 10000;

		# return the result:
		return float(ans)
