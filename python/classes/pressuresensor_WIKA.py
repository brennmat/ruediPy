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
import struct

from classes.misc	import misc

class pressuresensor_WIKA:
	"""
	ruediPy class for WIKA pressure sensor control.
	"""

	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'WIKA_PRESSURESENSOR' ):
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
		
		self.ser = ser

		self._label = label

		# configure pressure sensor for single pressure readings on request ("polling mode")
		cmd = 'SO\xFF' # command string to set polling mode
		cs = self.serial_checksum(cmd) # determine check sum
		self.ser.write(cmd + chr(cs) + '\r') # send command with check sum to serial port
		ans =  self.ser.read(5) # read out response to empty serial data buffer

		# get serial number of pressure sensor
		cmd = 'KN\x00' # command string to get serial number
		cs = self.serial_checksum(cmd) # determine check sum
		self.ser.write(cmd + chr(cs) + '\r') # send command with check sum to serial port
		self.ser.read(1) # first byte (not used)
		ans = self.ser.read(4) # four bytes of UNSIGNED32 number
		self.ser.read(2) # 6th and 7th byte (not used)
		self._serial_number = struct.unpack('<I',ans)[0] # convert to 4 bytes to integer
		print ('Successfully configured WIKA pressure sensor with serial number ' + str(self._serial_number) )

	
	########################################################################################################
	

	def serial_checksum(self,cmd):
		"""
		cs = pressuresensor_WIKA.serial_checksum( cmd )

		Return checksum used for serial port communication with WIKA pressure sensor.
		
		INPUT:
		cmd: serial-port command string without checksum

		OUTPUT:
		cs: checksum byte
		"""
		
		# sum of bytes:
		k = 0
		cs = 0

		while k < len(cmd):
			cs = cs + ord(cmd[k])
			k = k + 1

		# low byte:
		cs = cs & 0xFF

		# two's complement:
		cs = ( cs ^ 0xFF ) + 1
		
		return cs


	def label(self):
		"""
		label = pressuresensor_WIKA.label()

		Return label / name of the PRESSURESENSOR object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
	########################################################################################################
		

	def pressure(self,f):
		"""
		press,unit = pressuresensor_WIKA.pressure(f)
		
		Read out current pressure value (in hPa).
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		
		OUTPUT:
		press: pressure value in hPa (float)
		"""	

		cmd = 'PZ\x00' # command string to set polling mode
		cs = self.serial_checksum(cmd) # determine check sum
		self.ser.write(cmd + chr(cs) + '\r') # send command with check sum to serial port
		ans = self.ser.read(1) # first byte (not used)
		ans = self.ser.read(4) # four bytes of IEEE754 float number
		p = struct.unpack('<f',ans)[0] # convert to 4 bytes to float
		ans = self.ser.read(1) # unit
		self.ser.read(2) # last two bytes (not used)

		# convert to hPa
		if ans == '\xFF':
			unit = 'bar'
		elif ans == '\xFE':
			unit = 'bar-rel.'
		elif ans == '\x1F':
			unit = 'Psi'
		elif ans == '\x1E':
			unit = 'Psi-rel.'
		elif ans == '\xAF':
			unit = 'MPa'
		elif ans == '\xAE':
			unit = 'MPa-rel.'
		elif ans == '\xBF':
			unit = 'kg/cm2'
		elif ans == '\xBE':
			unit = 'kg/cm2-rel.'
		else:
			self.warning('WIKA pressure sensor returned unknown pressure unit')
		
		if not ( f == 'nofile' ):
			# get timestamp
			t = misc.nowUNIX()
			f.write_pressure('PRESSURESENSOR_WIKA',self.label(),p,unit,t)
			# self.warning('writing pressure value to data file is not yet implemented!')

		return p,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		pressuresensor_WIKA.warning(msg)
		
		Issue warning about issues related to operation of pressure sensor.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.warnmessage (self.label(),msg)

