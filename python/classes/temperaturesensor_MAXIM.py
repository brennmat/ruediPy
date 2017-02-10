# Code for the MAXIM DS1820 type temperature sensors.
# This is just a wrapper class for the pydigitemp package; you may need to install pydigitemp first. Your can run the following command to install pydigitemp: pip install https://github.com/neenar/pydigitemp/archive/master.zip
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
# Copyright 2016, 2917, Matthias Brennwald (brennmat@gmail.com)

from classes.misc	 import misc
from digitemp.master import UART_Adapter
from digitemp.device import AddressableDevice
from digitemp.device import DS18B20

class temperaturesensor_MAXIM:
	"""
	ruediPy class for MAXIM DS1820 type temperature sensors (wrapper class for pydigitemp package).
	"""


	########################################################################################################
	
	
	def __init__( self , serialport , romcode = '', label = 'TEMPERATURESENSOR' ):
		'''
		temperaturesensor_MAXIM.__init__( serialport , romcode, label = 'SELECTORVALVE' )
		
		Initialize TEMPERATURESENSOR object (MAXIM), configure serial port / 1-wire bus for connection to DS18B20 temperature sensor chip
		
		INPUT:
		serialport: device name of the serial port for 1-wire connection to the temperature sensor, e.g. serialport = '/dev/ttyUSB3'
		romcode: ROM code of the temperature sensor chip (you can find the ROM code using the digitemp program or using the pydigitemp package). If there is only a single temperature sensor connected to the 1-wire bus on the given serial port, romcode can be left empty.
		label (optional): label / name of the TEMPERATURESENSOR object (string). Default: label = 'TEMPERATURESENSOR'
		
		OUTPUT:
		(none)
		'''
		
		# configure 1-wire bus for communication with MAXIM temperature sensor chip
		r = AddressableDevice(UART_Adapter(serialport)).get_connected_ROMs()
		
		if r is None:
			print ('Couldn not find any 1-wire devices on ' + serialport)
		else:
			bus = UART_Adapter(serialport)
			if romcode == '':
				if len(r) == 1:
					# print ('Using 1-wire device ' + r[0] + '\n')
					self._sensor = DS18B20(bus)
					self._ROMcode = r[0]
				else:
					print ('Too many 1-wire devices to choose from! Try again with specific ROM code...')
					for i in range(1,len(r)):
						print ('Device ' + i + ' ROM code: ' + r[i-1] +'\n')
			else:
				self._sensor = DS18B20(bus, rom=romcode)
				self._ROMcode = romcode
		
		self._label = label
		
		if hasattr(self,'_sensor'):
			print ('Successfully configured DS18B20 temperature sensor (ROM code ' + self._ROMcode + ')' )
		else:
			self.warning('Could not initialize MAXIM DS1820 temperature sensor.')

	
	########################################################################################################


	def label(self):
		"""
		label = temperaturesensor_MAXIM.label()

		Return label / name of the TEMPERATURESENSOR object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
	########################################################################################################
		

	def temperature(self,f):
		"""
		temp,unit = temperaturesensor_MAXIM.temperature(f)
		
		Read out current temperaure value.
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		
		OUTPUT:
		temp: temperature value (float)
		unit: unit of temperature value (string)
		"""	

		temp = self._sensor.get_temperature()
		unit = 'deg.C'
		
		if not ( f == 'nofile' ):
			# get timestamp
			t = misc.now_UNIX()
			f.write_temperature('TEMPERATURESENSOR_MAXIM',self.label(),temp,unit,t)
		
		return temp,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		temperaturesensor_MAXIM.warning(msg)
		
		Issue warning about issues related to operation of pressure sensor.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.warnmessage (self.label(),msg)

