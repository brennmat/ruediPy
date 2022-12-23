# Code for the VIRTUAL type temperature sensors.
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
# Copyright 2016, 2017, Matthias Brennwald (brennmat@gmail.com)

try:
	import sys
	import warnings
	import numpy
	import os
	import time
	from classes.misc    import misc
	from digitemp.master import UART_Adapter
	from digitemp.device import AddressableDevice
	from digitemp.device import DS18B20
except ImportError as e:
	print (e)
	raise

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / temperaturesensor_VIRTUAL class is running on Python version < 3. Version 3.0 or newer is recommended!")


class temperaturesensor_VIRTUAL:
	"""
	ruediPy class for VIRTUAL type temperature sensors
	"""


	########################################################################################################
	
	
	def __init__( self , serialport , romcode = '', label = 'TEMPERATURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None, T_unit = 'deg.C' ):
		'''
		temperaturesensor_VIRTUAL.__init__( serialport , romcode, label = 'TEMPERATURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None )
		
		Initialize TEMPERATURESENSOR object (VIRTUAL)
		
		INPUT:
		serialport: device name of the serial port for 1-wire connection to the temperature sensor, e.g. serialport = '/dev/ttyUSB3'
		romcode: ROM code of the temperature sensor chip (you can find the ROM code using the digitemp program or using the pydigitemp package). If there is only a single temperature sensor connected to the 1-wire bus on the given serial port, romcode can be left empty.
		label (optional): label / name of the TEMPERATURESENSOR object (string) for data output. Default: label = 'TEMPERATURESENSOR'
		plot_title (optional): title string for use in plot window. If plot_title = None, the sensor label is used. Default: label = None
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches)
		has_external_plot_window (optional): flag to indicate if there is a GUI system that handles the plotting of the data buffer on its own. This flag can be set explicitly to True of False, or can use None to ask for automatic 'on the fly' check if the has_external_plot_window = True or False should be used. Default: has_external_plot_window = None
		T_unit: unit of T data (default: T_unit = 'deg.C')
		
		OUTPUT:
		(none)
		'''
		
		self._label = label
		
		if T_unit.upper() == 'DEG.C':
		    self._unit = 'deg.C'
		elif T_unit.upper() == 'DEG.F':
		    self._unit = 'deg.F'
		else:
		    self.warning( 'Could not initialize VIRTUAL temperature sensor: unit ' + T_unit + ' is not supported.')
		    
		# Check for has_external_plot_window flag:
		if has_external_plot_window is None:
			has_external_plot_window = misc.have_external_gui()

		# Check plot title:
		if plot_title == None:
			self._plot_title = self._label
		else:
			self._plot_title = plot_title

		# data buffer for temperature values:
		self._tempbuffer_t = numpy.array([])
		self._tempbuffer_T = numpy.array([])
		self._tempbuffer_unit = ['x'] * 0 # empty list
		self._tempbuffer_max_len = max_buffer_points
		self._tempbuffer_lastupdate_timestamp = -1

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

			# set up plotting environment
			self._fig = plt.figure(figsize=(fig_w,fig_h))
			t = 'VIRUTAL_TSENSOR'
			if self._plot_title:
				t = t + ' (' + self._plot_title + ')'
			self._fig.canvas.set_window_title(t)

			# set up panel for temperature history plot:
			self._tempbuffer_ax = plt.subplot(1,1,1)
			t = 'TEMPBUFFER'
			if self._plot_title:
				t = t + ' (' + self._plot_title + ')'
			self._tempbuffer_ax.set_title(t,loc="center")
			self._tempbuffer_ax.set_xlabel('Time (s)')
			self._tempbuffer_ax.set_ylabel('Temperature')
		
			# add (empty) line to plot (will be updated with data later):
			self._tempbuffer_ax.plot( [], [] , 'ko-' , markersize = 10 )

			# get some space in between panels to avoid overlapping labels / titles
			self._fig.tight_layout()
		
			# enable interactive mode:
			plt.ion()

			self._figwindow_is_shown = False


		print ( 'Successfully configured VIRTUAL temperature sensor.' )


	########################################################################################################


	def label(self):
		"""
		label = temperaturesensor_VIRTUAL.label()

		Return label / name of the TEMPERATURESENSOR object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		return self._label

	
	########################################################################################################
		

	def temperature(self,f,add_to_tempbuffer=True):
		"""
		temp,unit = temperaturesensor_VIRTUAL.temperature(f)
		
		Read out current temperaure value.
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		add_to_tempbuffer (optional): flag to indicate if data get appended to temperature buffer (default=True)

		OUTPUT:
		temp: temperature value (float)
		unit: unit of temperature value (string)
		"""	
		
		temp = 15 + (numpy.random.randn()-0.5)*5;
		unit = self._unit
		if unit.upper() == 'DEG.C':
		    pass
		elif unit.upper() == 'DEG.F':
		    # convert from deg.C to deg.F:
		    temp = (temp-32.0)*5/9
		else:
		    self.warning('T-Sensor data unit ' + unit + ' is not supported!')
		    temp = NA

		# get timestamp
		t = misc.now_UNIX()

		# add data to peakbuffer
		if add_to_tempbuffer:
			self.tempbuffer_add(t,temp,unit)

		# write data to datafile
		if not ( f == 'nofile' ):
			f.write_temperature('TEMPERATURESENSOR_VIRTUAL',self.label(),temp,unit,t)

		return temp,unit


	########################################################################################################
	

	def warning(self,msg):
		'''
		temperaturesensor_VIRTUAL.warning(msg)
		
		Issue warning about issues related to operation of pressure sensor.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.warnmessage ('[' + self.label() + '] ' + msg)


	########################################################################################################
	

	def tempbuffer_add(self,t,T,unit):
		"""
		temperaturesensor_VIRTUAL.tempbuffer_add(t,T,unit)
		
		Add data to temperature data buffer
				
		INPUT:
		t: epoch time
		T: temperature value
		unit: unit of pressure value (char/string)
		
		OUTPUT:
		(none)
		"""
				
		self._tempbuffer_t = numpy.append( self._tempbuffer_t , t )
		self._tempbuffer_T = numpy.append( self._tempbuffer_T , T )
		self._tempbuffer_unit.append( unit )

		N = self._tempbuffer_max_len
		
		if self._tempbuffer_t.shape[0] > N:
			self._tempbuffer_t    = self._tempbuffer_t[-N:]
			self._tempbuffer_T    = self._tempbuffer_T[-N:]
			self._tempbuffer_unit = self._tempbuffer_unit[-N:]

		self._tempbuffer_lastupdate_timestamp = misc.now_UNIX()


	########################################################################################################


	def tempbuffer_get_timestamp(self):
		"""
		timestamp = temperaturesensor_VIRTUAL.tempbuffer_get_timestamp()

		Get time stamp of last update to tempbuffer data
		
		INPUT:
		(none)

		OUTPUT:
		timestamp: UNIX time of last update
		"""

		return self._tempbuffer_lastupdate_timestamp


	########################################################################################################


	def plot_tempbuffer(self):
		'''
		temperaturesensor_VIRTUAL.plot_tempbuffer()

		Plot trend (or update plot) of values in temperature data buffer (e.g. after adding data)
		NOTE: plotting may be slow, and it may therefore be a good idea to keep the update interval low to avoid affecting the duty cycle.

		INPUT:
		(none)

		OUTPUT:
		(none)
		'''

		if not self._has_display:
			self.warning('Plotting of tempbuffer trend not possible (no display system available).')

		else:

			try: # make sure data analysis does not fail due to a silly plotting issue

				if not self._figwindow_is_shown:
					# show the window on screen
					self._fig.show()
					self._figwindow_is_shown = True

				# Set plot data:
				t0 = misc.now_UNIX()
				self._tempbuffer_ax.lines[0].set_data( self._tempbuffer_t - t0 , self._tempbuffer_T )

				# Scale axes:
				self._tempbuffer_ax.relim()
				self._tempbuffer_ax.autoscale_view()
				
				# set title and axis labels:
				t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(t0))
				t = 'TEMPBUFFER'
				if self._plot_title:
					t = t + ' (' + self._plot_title + ')'
				self._tempbuffer_ax.set_title(t + ' at ' + t0)

				# Get temperature units right:
				self._tempbuffer_ax.set_ylabel('Temperature (' + str(self._tempbuffer_unit[0]) + ')' )

				# Update the plot:
				# self._fig.canvas.draw()
				self._fig.canvas.flush_events()

			except:
				self.warning( 'Error during plotting of tempbuffer trend (' + str(sys.exc_info()[0]) + ').' )


	########################################################################################################


	def tempbuffer_clear(self):
		"""
		temperaturesensor_VIRTUAL.pressbuffer_clear()

		Clear the buffer of temperature readings

		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		# clear data buffer for TEMPERATURE values:
		self._tempbuffer_t = self._tempbuffer_t[[]]
		self._tempbuffer_T = self._tempbuffer_T[[]]
		self._tempbuffer_unit = ['x'] * 0 # empty list
		self._tempbuffer_lastupdate_timestamp = misc.now_UNIX()



	########################################################################################################
