# Code for the WIKA pressure sensor class
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
	import struct
	import numpy
	import os
except ImportError as e:
	print (e)
	raise

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / pressuresensor_WIKA class is running on Python version < 3. Version 3.0 or newer is recommended!")

from .misc	import misc


class pressuresensor_WIKA:
	"""
	ruediPy class for WIKA pressure sensor control.
	"""

	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'PRESSURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None, P_unit = 'bar'):
		'''
		pressuresensor_WIKA.__init__( serialport , label = 'PRESSURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None, P_unit = 'bar' )
		
		Initialize PRESSURESENSOR object (WIKA), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. serialport = '/dev/ttyUSB3'
		label (optional): label / name of the PRESSURESENSOR object (string). Default: label = 'PRESSURESENSOR'
		plot_title (optional): title string for use in plot window. If plot_title = None, the sensor label is used. Default: label = None
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches)
		has_external_plot_window (optional): flag to indicate if there is a GUI system that handles the plotting of the data buffer on its own. This flag can be set explicitly to True of False, or can use None to ask for automatic 'on the fly' check if the has_external_plot_window = True or False should be used. Default: has_external_plot_window = None
		P_unit: unit of P data (default: P_unit = 'bar')
		
		OUTPUT:
		(none)
		'''
	
		self._label = label

		if P_unit.upper() == 'HPA':
		    self._unit = 'hPa'
		elif P_unit.upper() == 'BAR':
		    self._unit = 'bar'
		elif P_unit.upper() == 'MBAR':
		    self._unit = 'mbar'
		elif P_unit.upper() == 'ATM':
		    self._unit = 'atm'
		else:
		    self.warning( 'Could not initialize WIKA pressure sensor: unit ' + P_unit + ' is not supported.')

		# Check for has_external_plot_window flag:
		if has_external_plot_window is None:
				has_external_plot_window = misc.have_external_gui() 

		# Check plot title:
		if plot_title == None:
			self._plot_title = self._label
		else:
			self._plot_title = plot_title

		# data buffer for PEAK values:
		self._pressbuffer_t = numpy.array([])
		self._pressbuffer_p = numpy.array([])
		self._pressbuffer_unit = ['x'] * 0 # empty list
		self._pressbuffer_max_len = max_buffer_points
		self._pressbuffer_lastupdate_timestamp = -1
		
		# set up plotting environment
		if has_external_plot_window:
			# no need to set up plotting
			self._has_external_display = True
			self._has_display = False
		else:
			self._has_external_display = False
			self._has_display = misc.plotting_setup() # check for graphical environment, import matplotlib

		try:
			# open and configure serial port for communication with WIKA pressure sensor (9600 baud, 8 data bits, no parity, 1 stop bit

			from pkg_resources import parse_version
			if parse_version(serial.__version__) >= parse_version('3.3') :
				# open port with exclusive access:
				ser = serial.Serial(
					port     = serialport,
					baudrate = 9600,
					parity   = serial.PARITY_NONE,
					stopbits = serial.STOPBITS_ONE,
					bytesize = serial.EIGHTBITS,
					timeout  = 5,
					exclusive = True
				)

			else:
				# open port (can't ask for exclusive access):
				ser = serial.Serial(
					port     = serialport,
					baudrate = 9600,
					parity   = serial.PARITY_NONE,
					stopbits = serial.STOPBITS_ONE,
					bytesize = serial.EIGHTBITS,
					timeout  = 5
				)

			ser.flushOutput()	# make sure output is empty
			time.sleep(0.1)
			ser.flushInput()	# make sure input is empty
		
			self.ser = ser
			self._ser_locked = False

			# configure pressure sensor for single pressure readings on request ("polling mode")
			cmd = 'SO\xFF' # command string) (byte to set polling mode
			cs = self.serial_checksum(cmd) # determine check sum
			self.get_serial_lock()
			self.ser.write((cmd + chr(cs) + '\r').encode('utf-8')) # send command with check sum to serial port
			ans = self.ser.read(5) # read out response to empty serial data buffer

			# get serial number of pressure sensor
			cmd = 'KN\x00' # command string to get serial number
			cs = self.serial_checksum(cmd) # determine check sum
			self.ser.write((cmd + chr(cs) + '\r').encode('utf-8')) # send command with check sum to serial port
			self.ser.read(1) # first byte (not used)
			ans = self.ser.read(4) # four bytes of UNSIGNED32 number
			self.ser.read(2) # 6th and 7th byte (not used)
			self.release_serial_lock()
			
			self._serial_number = struct.unpack('<I',ans)[0] # convert to 4 bytes to integer
	
			if self._has_display: # prepare plotting environment and figure

				import matplotlib.pyplot as plt

				# set up plot figure:
				self._fig = plt.figure(figsize=(fig_w,fig_h))
				t = 'WIKA P30'
				if self._plot_title:
					t = t + ' (' + self._plot_title + ')'
				self._fig.canvas.set_window_title(t)

				# set up panel for pressure history plot:
				self._pressbuffer_ax = plt.subplot(1,1,1)
				t = 'PRESSBUFFER'
				if self._plot_title:
					t = t + ' (' + self._plot_title + ')'
				self._pressbuffer_ax.set_title(t,loc="center")
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
	

	def get_serial_lock(self):
		'''
		pressuresensor_WIKA._get_serial_lock()
		
		Lock serial port for exclusive access (important if different threads / processes are trying to use the port). Make sure to release the lock after using the port (see pressuresensor_WIKA._release_serial_lock()!
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# wait until the serial port is unlocked:
		while self._ser_locked == True:
			time.sleep(0.01)
			
		# lock the port:
		self._ser_locked = True
		

	
########################################################################################################
	


	def release_serial_lock(self):
		'''
		pressuresensor_WIKA._release_serial_lock()
		
		Release lock on serial port.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# release the lock:
		self._ser_locked = False



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
				self.get_serial_lock()
				self.ser.write((cmd + chr(cs) + '\r').encode('utf-8')) # send command with check sum to serial port
				ans = self.ser.read(1) # first byte (not used)
				ans = self.ser.read(4) # four bytes of IEEE754 float number
				p = struct.unpack('<f',ans)[0] # convert to 4 bytes to float
				ans = self.ser.read(1) # unit
				self.ser.read(2) # last two bytes (not used)
				self.release_serial_lock()
		
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
				
				# convert to bar:
				if unit == 'bar':
				    pass
				elif unit == 'bar-rel':
				    pass
				elif unit == 'Psi':
				    p = p/14.5038
				elif unit == 'Psi-rel':
				    p = p/14.5038
				elif unit == 'MPa':
				    p = 10.0*p
				elif unit == 'MPa-rel':
				    p = 10.0*p
				elif unit == 'kg/cm2':
				    p = 0.980665*p
				elif unit == 'kg/cm2-rel':
				    p = 0.980665*p
				else:
				    self.warning('Cannot convert data from WIKA P-sensor unit, unknown unit ' + unit)
				    p = NA

				# convert from bar to desired unit (if necessary):
				if self._unit.upper() == 'BAR':
				    pass
				elif self._unit.upper() == 'MBAR':
				    p = 1000.0*p
				elif self._unit.upper() == 'HPA':
				    p = 1000.0*p
				elif self._unit.upper() == 'ATM':
				    p = p / 1.01325
				else:
				    self.warning('P-Sensor data unit ' + self._unit + ' is not supported!')
				    p = NA
				unit = self._unit






				# add data to peakbuffer
				if add_to_pressbuffer:
					self.pressbuffer_add(t,p,unit)

			except:
				self.release_serial_lock()
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
		
		misc.warnmessage ('[' + self.label() + '] ' + msg)


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
			self._pressbuffer_t    = self._pressbuffer_t[-N:]
			self._pressbuffer_p    = self._pressbuffer_p[-N:]
			self._pressbuffer_unit = self._pressbuffer_unit[-N:]

		self._pressbuffer_lastupdate_timestamp = misc.now_UNIX()


	########################################################################################################


	def pressbuffer_get_timestamp(self):
		"""
		timestamp = pressuresensor_WIKA.pressbuffer_get_timestamp()

		Get time stamp of last update to pressbuffer data
		
		INPUT:
		(none)

		OUTPUT:
		timestamp: UNIX time of last update
		"""

		return self._pressbuffer_lastupdate_timestamp
		

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
				t = 'PRESSBUFFER'
				if self._plot_title:
					t = t + ' (' + self._plot_title + ')'
				self._pressbuffer_ax.set_title(t + ' at ' + t0)

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
			self._pressbuffer_lastupdate_timestamp = misc.now_UNIX()


	########################################################################################################
