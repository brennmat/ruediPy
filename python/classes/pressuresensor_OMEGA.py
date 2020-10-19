# Code for the OMEGA pressure sensor class
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
# Copyright 2016, 2017, 2018 Matthias Brennwald (brennmat@gmail.com)

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
	warnings.warn("ruediPy / pressuresensor_OMEGA class is running on Python version < 3. Version 3.0 or newer is recommended!")

from classes.misc	import misc


havedisplay = "DISPLAY" in os.environ
if havedisplay: # prepare plotting environment
	try:
		import matplotlib
		matplotlib.rcParams['legend.numpoints'] = 1
		matplotlib.rcParams['axes.formatter.useoffset'] = False
		# suppress mplDeprecation warning:
		import warnings
		import matplotlib.cbook
		warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
		matplotlib.use('TkAgg')
		import matplotlib.pyplot as plt
	except:
		misc.warnmessage ('OMEGA-PRESSURE init','Could not set up display environment.')
		havedisplay = False

class pressuresensor_OMEGA:
	"""
	ruediPy class for OMEGA pressure sensor control.
	"""

	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'PRESSURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5):
		'''
		pressuresensor_OMEGA.__init__( serialport , label = 'PRESSURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 3 , fig_h = 2 )
		
		Initialize PRESSURESENSOR object (OMEGA), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. serialport = '/dev/ttyUSB3'
		label (optional): label / name of the PRESSURESENSOR object for data output (string). Default: label = 'PRESSURESENSOR'
		plot_title (optional): title string for use in plot window. If plot_title = None, the sensor label is used. Default: label = None
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches)

		
		OUTPUT:
		(none)
		'''
	
		self._label = label
		self._has_display = havedisplay

		if plot_title == None:
			self._plot_title = self._label
		else:
			self._plot_title = plot_title

		try:

			# open and configure serial port for communication with VICI valve (9600 baud, 8 data bits, no parity, 1 stop bit

			from pkg_resources import parse_version
			if parse_version(serial.__version__) >= parse_version('3.3') :
				# open port with exclusive access:
				ser = serial.Serial(
					port     = serialport,
					baudrate = 115200,
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
					baudrate = 115200,
					parity   = serial.PARITY_NONE,
					stopbits = serial.STOPBITS_ONE,
					bytesize = serial.EIGHTBITS,
					timeout  = 5
				)

			ser.flushOutput()   # make sure output is empty
			time.sleep(0.1)
			ser.flushInput()    # make sure input is empty
		
			self.ser = ser

			# get serial number of pressure sensor
			self.ser.write(('SNR\r').encode('utf-8')) # send command with check sum to serial port
			ans = self.ser.readline().decode('utf-8') # read response and decode ASCII	
			ser.flushInput()   # make sure input is empty
			self._serial_number = int(ans.rstrip().split('=')[1]) # parse response to integer number

			# data buffer for PEAK values:
			self._pressbuffer_t = numpy.array([])
			self._pressbuffer_p = numpy.array([])
			self._pressbuffer_unit = ['x'] * 0 # empty list
			self._pressbuffer_max_len = max_buffer_points
	
			# set up plotting environment
			if self._has_display: # prepare plotting environment and figure

				# set up plot figure:
				self._fig = plt.figure(figsize=(fig_w,fig_h))
				t = 'OMEGA PXM409'
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

			print ('Successfully configured OMEGA pressure sensor with serial number ' + str(self._serial_number) + ' on ' + serialport )


		except:
			self.warning ( 'An error occured during configuration of the pressure sensor at serial interface ' + serialport + '. The pressure sensor cannot be used.' )



	########################################################################################################

		

	def label(self):
		"""
		label = pressuresensor_OMEGA.label()

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
		press,unit = pressuresensor_OMEGA.pressure(f,add_to_pressbuffer=True)
		
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
				# get pressure reading from the sensor:
				self.ser.write(('P\r').encode('utf-8')) # send command to serial port
				ans =  self.ser.readline().decode('utf-8') # read response and decode ASCII
				if ans[0] == '>':
					# fix > character dangling in the serial buffer from previous reading
					ans = ans[1:]
				self.ser.flushInput()  # make sure input is empty
				
				ans = ans.split(' ')
				p = float( ans[0] )    # convert string to float
				unit = ans[1]
				if unit != 'bar':
					raise ValueError( 'OMEGA pressure sensor returned unit = ' + unit + ', not bar!')
				else:
					# convert to mbar = hPa:
					p = 1000 * p
					unit = 'hPa'
						
				# get timestamp
				t = misc.now_UNIX()

				# add data to peakbuffer
				if add_to_pressbuffer:
					self.pressbuffer_add(t,p,unit)

			except ValueError as e:
				self.warning( e )
			except:
				self.warning( 'An unknown error occured while reading the OMEGA pressure sensor!' )

		# write data to datafile
		if not ( f == 'nofile' ):
			f.write_pressure('PRESSURESENSOR_WIKA',self.label(),p,unit,t)

		return p,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		pressuresensor_OMEGA.warning(msg)
		
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
		pressuresensor_OMEGA.pressbuffer_add(t,p,unit)
		
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



	########################################################################################################


	def plot_pressbuffer(self):
		'''
		pressuresensor_OMEGA.plot_pressbuffer()

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
		pressuresensor_OMEGA.pressbuffer_clear()

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
