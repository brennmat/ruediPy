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
# Copyright 2016, 2017, Matthias Brennwald (brennmat@gmail.com)

import sys
import warnings
import serial
import time
import struct
import numpy
import os

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / pressuresensor_WIKA class is running on Python version < 3. Version 3.0 or newer is recommended!")

from classes.misc	import misc

havedisplay = "DISPLAY" in os.environ
if havedisplay: # prepare plotting environment
	import matplotlib
	matplotlib.rcParams['legend.numpoints'] = 1
	matplotlib.rcParams['axes.formatter.useoffset'] = False
	# suppress mplDeprecation warning:
	import warnings
	import matplotlib.cbook
	warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
	matplotlib.use('TkAgg')
	import matplotlib.pyplot as plt

class pressuresensor_WIKA:
	"""
	ruediPy class for WIKA pressure sensor control.
	"""

	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'PRESSURESENSOR' , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5):
		'''
		pressuresensor_WIKA.__init__( serialport , label = 'PRESSURESENSOR' , max_buffer_points = 500 , fig_w = 3 , fig_h = 2 )
		
		Initialize PRESSURESENSOR object (WIKA), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. serialport = '/dev/ttyUSB3'
		label (optional): label / name of the PRESSURESENSOR object (string). Default: label = 'PRESSURESENSOR'
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches)

		
		OUTPUT:
		(none)
		'''
	
		self._label = label
		self._has_display = havedisplay

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
		
			self.ser = ser

			# configure pressure sensor for single pressure readings on request ("polling mode")
			cmd = 'SO\xFF' # command string) (byte to set polling mode
			cs = self.serial_checksum(cmd) # determine check sum
		
			self.ser.write((cmd + chr(cs) + '\r').encode('utf-8')) # send command with check sum to serial port
			ans =  self.ser.read(5) # read out response to empty serial data buffer

			# get serial number of pressure sensor
			cmd = 'KN\x00' # command string to get serial number
			cs = self.serial_checksum(cmd) # determine check sum
			self.ser.write((cmd + chr(cs) + '\r').encode('utf-8')) # send command with check sum to serial port
			self.ser.read(1) # first byte (not used)
			ans = self.ser.read(4) # four bytes of UNSIGNED32 number
			self.ser.read(2) # 6th and 7th byte (not used)
			self._serial_number = struct.unpack('<I',ans)[0] # convert to 4 bytes to integer
	

			# data buffer for PEAK values:
			self._pressbuffer_t = numpy.array([])
			self._pressbuffer_p = numpy.array([])
			self._pressbuffer_unit = ['x'] * 0 # empty list
			self._pressbuffer_max_len = max_buffer_points
	
			# set up plotting environment
			if self._has_display: # prepare plotting environment and figure

				# set up plot figure:
				self._fig = plt.figure(figsize=(fig_w,fig_h))
				t = 'WIKA P30'
				if self._label:
					t = t + ' (' + self.label() + ')'
				self._fig.canvas.set_window_title(t)

				# set up panel for pressure history plot:
				self._pressbuffer_ax = plt.subplot(1,1,1)
				self._pressbuffer_ax.set_title('PRESSBUFFER (' + self.label() + ')',loc="center")
				self._pressbuffer_ax.set_xlabel('Time (s)')
				self._pressbuffer_ax.set_ylabel('Pressure')

				# add (empty) line to plot (will be updated with data later):
				self._pressbuffer_ax.plot( [], [] , 'ko-' , markersize = 10 )

				# get some space in between panels to avoid overlapping labels / titles
				self._fig.tight_layout()
			
				# enable interactive mode:
				plt.ion()

				self._figwindow_is_shown = False

			print ('Successfully configured WIKA pressure sensor with serial number ' + str(self._serial_number) + ' on ' + serialport )


		except:
			# print ( '\n**** WARNING: An error occured during configuration of the pressure sensor at serial interface ' + serialport + '. The pressure sensor cannot be used.\n' )
			self.warning ( 'An error occured during configuration of the pressure sensor at serial interface ' + serialport + '. The pressure sensor cannot be used.' )


	
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

	
	########################################################################################################
		

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
		

	def pressure(self,f,add_to_pressbuffer=True):
		"""
		press,unit = pressuresensor_WIKA.pressure(f,add_to_pressbuffer=True)
		
		Read out current pressure value.
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		add_to_pressbuffer (optional): flag to indicate if data get appended to pressure buffer (default=True)

		OUTPUT:
		press: pressure value in hPa (float)
		unit: unit of pressure value (string)
		"""	

		p = None;
		unit = '?';
		t = misc.now_UNIX()
		if not(hasattr(self,'ser')):
			self.warning( 'sensor is not initialised, could not read data.' )
		else:
			try:
				cmd = 'PZ\x00' # command string to set polling mode
				cs = self.serial_checksum(cmd) # determine check sum
				self.ser.write((cmd + chr(cs) + '\r').encode('utf-8')) # send command with check sum to serial port
				ans = self.ser.read(1) # first byte (not used)
				ans = self.ser.read(4) # four bytes of IEEE754 float number
				p = struct.unpack('<f',ans)[0] # convert to 4 bytes to float
				ans = self.ser.read(1) # unit
				self.ser.read(2) # last two bytes (not used)
		
				# get timestamp
				t = misc.now_UNIX()

				# get unit:
				if ans == b'\xFF':
					unit = 'bar'
				elif ans == b'\xFE':
					unit = 'bar-rel.'
				elif ans == b'\x1F':
					unit = 'Psi'
				elif ans == b'\x1E':
					unit = 'Psi-rel.'
				elif ans == b'\xAF':
					unit = 'MPa'
				elif ans == b'\xAE':
					unit = 'MPa-rel.'
				elif ans == b'\xBF':
					unit = 'kg/cm2'
				elif ans == b'\xBE':
					unit = 'kg/cm2-rel.'
				else:
					self.warning('WIKA pressure sensor returned unknown pressure unit')
					unit = '???'

				# add data to peakbuffer
				if add_to_pressbuffer:
					self.pressbuffer_add(t,p,unit)

			except:
				self.warning( 'could not read sensor!' )

		# write data to datafile
		if not ( f == 'nofile' ):
			f.write_pressure('PRESSURESENSOR_WIKA',self.label(),p,unit,t)

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


	########################################################################################################
	

	def pressbuffer_add(self,t,p,unit):
		"""
		pressuresensor_WIKA.pressbuffer_add(t,p,unit)
		
		Add data to pressure data buffer
				
		INPUT:
		t: epoch time
		p: pressure value
		unit: unit of pressure value (char/string)
		
		OUTPUT:
		(none)
		"""
				
		self._pressbuffer_t = numpy.append( self._pressbuffer_t , t )
		self._pressbuffer_p = numpy.append( self._pressbuffer_p , p )
		self._pressbuffer_unit.append( unit )

		N = self._pressbuffer_max_len
		
		if self._pressbuffer_t.shape[0] > N:
			self._pressbuffer_t 	     = self._pressbuffer_t[-N:]
			self._pressbuffer_p 	     = self._pressbuffer_p[-N:]
			self._pressbuffer_unit       = self._pressbuffer_unit[-N:]



	########################################################################################################


	def plot_pressbuffer(self):
		'''
		pressuresensor_WIKA.plot_pressbuffer()

		Plot trend (or update plot) of values in pressure data buffer (e.g. after adding data)
		NOTE: plotting may be slow, and it may therefore be a good idea to keep the update interval low to avoid affecting the duty cycle.

		INPUT:
		(none)

		OUTPUT:
		(none)
		'''

		if not self._has_display:
			self.warning('Plotting of pressbuffer trend not possible (no display system available).')

		else:

			try: # make sure data analysis does not fail due to a silly plotting issue

				if not self._figwindow_is_shown:
					# show the window on screen
					self._fig.show()
					self._figwindow_is_shown = True

				# Set plot data:
				t0 = misc.now_UNIX()
				self._pressbuffer_ax.lines[0].set_data( self._pressbuffer_t - t0 , self._pressbuffer_p )

				# Scale axes:
				self._pressbuffer_ax.relim()
				self._pressbuffer_ax.autoscale_view()
				
				# set title and axis labels:
				t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(t0))
				self._pressbuffer_ax.set_title('PRESSBUFFER (' + self.label() + ') at ' + t0)

				# Get pressure units right:
				self._pressbuffer_ax.set_ylabel('Pressure (' + str(self._pressbuffer_unit[0]) + ')' )

				# Update the plot:
				# self._fig.canvas.draw()
				self._fig.canvas.flush_events()

			except:
				self.warning( 'Error during plotting of pressbuffer trend (' + str(sys.exc_info()[0]) + ').' )


	########################################################################################################


	def pressbuffer_clear(self):
		"""
		pressuresensor_WIKA.pressbuffer_clear()

		Clear the buffer of pressure readings

		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		# clear data buffer for PRESSURE values:
		if not(hasattr(self,'ser')):
			self.warning( 'sensor is not initialised, could not clear data buffer.' )
		else:
			self._pressbuffer_t = self._pressbuffer_t[[]]
			self._pressbuffer_p = self._pressbuffer_p[[]]
			self._pressbuffer_unit = ['x'] * 0 # empty list



	########################################################################################################
