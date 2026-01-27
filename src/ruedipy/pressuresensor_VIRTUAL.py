# Code for the VIRTUAL pressure sensor class
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
	warnings.warn("ruediPy / pressuresensor_VIRTUAL class is running on Python version < 3. Version 3.0 or newer is recommended!")

from classes.misc	import misc


class pressuresensor_VIRTUAL:
	"""
	ruediPy class for VIRTUAL pressure sensor control.
	"""

	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'PRESSURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None, P_unit = 'bar'):
		'''
		pressuresensor_VIRTUAL.__init__( serialport , label = 'PRESSURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None, P_unit = 'bar' )
		
		Initialize PRESSURESENSOR object (VIRTUAL), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. serialport = '/dev/ttyUSB3'
		label (optional): label / name of the PRESSURESENSOR object for data output (string). Default: label = 'PRESSURESENSOR'
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
		    self.warning( 'Could not initialize OMEGA pressure sensor: unit ' + P_unit + ' is not supported.')
		
		# Check for has_external_plot_window flag:
		if has_external_plot_window is None:
			has_external_plot_window = misc.have_external_gui() 

		# Check plot title:
		if plot_title == None:
			self._plot_title = self._label
		else:
			self._plot_title = plot_title
			
		self._serial_number = 123456789

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

		if self._has_display: # prepare plotting environment and figure
		
			import matplotlib.pyplot as plt

			# set up plot figure:
			self._fig = plt.figure(figsize=(fig_w,fig_h))
			t = 'VIRTUAL_PSENSOR'
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

		print ('Successfully configured VIRTUAL pressure sensor with serial number ' + str(self._serial_number) + '.' )



	########################################################################################################

		

	def label(self):
		"""
		label = pressuresensor_VIRTUAL.label()

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
		press,unit = pressuresensor_VIRTUAL.pressure(f,add_to_pressbuffer=True)
		
		Read out current pressure value.
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		add_to_pressbuffer (optional): flag to indicate if data get appended to pressure buffer (default=True)

		OUTPUT:
		press: pressure value in hPa (float)
		unit: unit of pressure value (string)
		"""	

		p = 1.0 + (numpy.random.randn()-0.5)*0.05;
		unit = 'bar';

		# get timestamp
		t = misc.now_UNIX()

		# convert unit (if necessary):
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

		# write data to datafile
		if not ( f == 'nofile' ):
			f.write_pressure('PRESSURESENSOR_VIRTUAL',self.label(),p,unit,t)

		return p,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		pressuresensor_VIRTUAL.warning(msg)
		
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
		pressuresensor_VIRTUAL.pressbuffer_add(t,p,unit)
		
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
		timestamp = pressuresensor_VIRTUAL.pressbuffer_get_timestamp()

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
		pressuresensor_VIRTUAL.plot_pressbuffer()

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
		pressuresensor_VIRTUAL.pressbuffer_clear()

		Clear the buffer of pressure readings

		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		# clear data buffer for PRESSURE values:
		self._pressbuffer_t = self._pressbuffer_t[[]]
		self._pressbuffer_p = self._pressbuffer_p[[]]
		self._pressbuffer_unit = ['x'] * 0 # empty list
		self._pressbuffer_lastupdate_timestamp = misc.now_UNIX()


	########################################################################################################
