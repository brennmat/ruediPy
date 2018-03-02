# Code for the VICI selector valve class
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

import sys
import warnings
import serial
import time
from classes.misc	import misc

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / selectorvalve_VICI class is running on Python version < 3. Version 3.0 or newer is recommended!")


class selectorvalve_VICI:
	"""
	ruediPy class for VICI valve control. This assumes the serial protocol used with VICI's older "microlectric" actuators. For use with the newer "universal" actuators, they must be set to "legacy mode" using the "LG1" command (see page 8 of VICI document "Universal Electric Actuator Instruction Manual"). The self.set_legacy command may be useful for this.
	"""
	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'SELECTORVALVE' ):
		'''
		selectorvalve.__init__( serialport , label = 'SELECTORVALVE' )
		
		Initialize SELECTORVALVE object (VICI valve), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. P = '/dev/ttyUSB3'
		label (optional): label / name of the SELECTORVALVE object (string). Default: label = 'SELECTORVALVE'
		
		OUTPUT:
		(none)
		'''

		try:
			# open and configure serial port for communication with VICI valve (9600 baud, 8 data bits, no parity, 1 stop bit
			ser = serial.Serial(
				port     = serialport,
				baudrate = 9600,
				parity   = serial.PARITY_NONE,
				stopbits = serial.STOPBITS_ONE,
				bytesize = serial.EIGHTBITS,
				timeout  = 5.0
			)
			ser.flushOutput() 	# make sure output is empty
			time.sleep(0.1)
			ser.flushInput() 	# make sure input is empty
		
			self.ser = ser;

			self._label = label
		
			print ( 'Successfully configured VICI selector valve on ' + serialport )

		except serial.SerialException as e:
			print( 'Could not establish connection to VICI selectorvalve:' , e )
			sys.exit(1)

		except:
			print( 'Unexpected error during initialisation of VICI selectorvalve:', sys.exc_info()[0] )
			sys.exit(1)

	########################################################################################################
	

	def label(self):
		"""
		label = selectorvalve_VICI.label()

		Return label / name of the SELECTORVALVE object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
	

	def warning(self,msg):
		# warn about issues related to operation of the valve
		# msg: warning message
		misc.warnmessage ('VICI VALVE',msg)

	
	########################################################################################################
	

	def set_legacy(self):
		'''
		selectorvalve_VICI.set_legacy()

		Set communication protocol to LEGACY mode (useful to make the newer valve controlers compatible with the LEGACY protocol).

		INPUT:
		(none)
   
		OUTPUT:
		(none)
		'''
		
		self.ser.write(('LG1\r\n').encode('ascii'))
		
		time.sleep(0.5)


	########################################################################################################
	

	def setpos(self,val,f):
		'''
		selectorvalve_VICI.setpos(val,f)

		Set valve position

		INPUT:
		val: new valve position (integer)
		f: datafile object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.

		OUTPUT:
		(none)
		'''
		
		val = int(val)
		curpos = self.getpos()
		if not curpos == val: # check if valve is already at desired position
			# send command to serial port:
			self.ser.write(('GO' + str(val) + '\r\n').encode('ascii'))
		
		# write to datafile
		if not f == 'nofile':
			f.write_valve_pos('SELECTORVALVE_VICI',self.label(),val,misc.now_UNIX())

		# give the valve some time to actually do the switch:
		time.sleep(0.5)


	########################################################################################################
	

	def getpos(self):
		'''
		pos = selectorvalve_VICI.getpos()

		Get valve position

		INPUT:
		(none)

		OUTPUT:
		pos: valve postion (integer)
		'''
		
		# make sure serial port buffer is empty:
		self.ser.flushInput() 	#pot make sure input is empty
		self.ser.flushOutput() 	# make sure output is empty

		# send command to serial port:
		self.ser.write('CP\r\n'.encode('ascii'))
		
		# wait for response
		t = 0
		dt = 0.1
		doWait = 1
		while doWait:
			if self.ser.inWaiting() == 0: # wait
				time.sleep(dt)
				t = t + dt
				if t > 5: # give up waiting
					doWait = 0
					self.warning('could not determine valve position (no response from valve)')
					ans = '-1'
			else:
				doWait = 0
				ans = ''
		
		# read back result:
		if (ans != '-1'):
			while self.ser.inWaiting() > 0: # while there's something in the buffer...
				ans = ans + self.ser.read().decode('ascii') # read each byte
		
		try:
			# print ans
			ans = ans.split('=')[1] # split answer in the form 'Position is  = 1'
			ans = ans.strip() # strip away whitespace
		except:
			self.warning('could not parse response from valve: ans = ' + ans)
			ans = '?'
	    	
	    # check result:
		if not ans.isdigit():
			self.warning('could not determine valve position (position = ' + ans + ')')
			ans = '-1'

		# return the result:
		return int(ans)
