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
	warnings.warn("ruediPy / temperaturesensor_MAXIM class is running on Python version < 3. Version 3.0 or newer is recommended!")


class temperaturesensor_MAXIM:
	"""
	ruediPy class for MAXIM DS1820 type temperature sensors (wrapper class for pydigitemp package).
	"""


	########################################################################################################
	
	
	def __init__( self , serialport , romcode = '', label = 'TEMPERATURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None):
		'''
		temperaturesensor_MAXIM.__init__( serialport , romcode, label = 'TEMPERATURESENSOR' , plot_title = None , max_buffer_points = 500 , fig_w = 6.5 , fig_h = 5 , has_plot_window = True , has_external_plot_window = None )
		
		Initialize TEMPERATURESENSOR object (MAXIM), configure serial port / 1-wire bus for connection to DS18B20 temperature sensor chip
		
		INPUT:
		serialport: device name of the serial port for 1-wire connection to the temperature sensor, e.g. serialport = '/dev/ttyUSB3'
		romcode: ROM code of the temperature sensor chip (you can find the ROM code using the digitemp program or using the pydigitemp package). If there is only a single temperature sensor connected to the 1-wire bus on the given serial port, romcode can be left empty.
		label (optional): label / name of the TEMPERATURESENSOR object (string) for data output. Default: label = 'TEMPERATURESENSOR'
		plot_title (optional): title string for use in plot window. If plot_title = None, the sensor label is used. Default: label = None
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches)
		has_external_plot_window (optional): flag to indicate if there is a GUI system that handles the plotting of the data buffer on its own. This flag can be set explicitly to True of False, or can use None to ask for automatic 'on the fly' check if the has_external_plot_window = True or False should be used. Default: has_external_plot_window = None
		
		OUTPUT:
		(none)
		'''
		
		self._label = label
		
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

		try:

			# configure 1-wire bus for communication with MAXIM temperature sensor chip
			r = AddressableDevice(UART_Adapter(serialport)).get_connected_ROMs()

			if r is None:
				print ( 'Couldn not find any 1-wire devices on ' + serialport )
			else:
				bus = UART_Adapter(serialport)
				if romcode == '':
					if len(r) == 1:
						# print ('Using 1-wire device ' + r[0] + '\n')
						self._sensor = DS18B20(bus)
						self._ROMcode = r[0]
					else:
						print ( 'Too many 1-wire devices to choose from! Try again with specific ROM code...' )
						for i in range(1,len(r)):
							print ( 'Device ' + i + ' ROM code: ' + r[i-1] +'\n' )
				else:
					self._sensor = DS18B20(bus, rom=romcode)
					self._ROMcode = romcode
				
				self._UART_locked = False
		
			if self._has_display: # prepare plotting environment and figure

				import matplotlib.pyplot as plt

				# set up plotting environment
				self._fig = plt.figure(figsize=(fig_w,fig_h))
				t = 'MAXIM DS1820'
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


			if hasattr(self,'_sensor'):
				print ( 'Successfully configured DS18B20 temperature sensor (ROM code ' + self._ROMcode + ')' )
			else:
				self.warning( 'Could not initialize MAXIM DS1820 temperature sensor.' )


		except:
			# print ( '\n**** WARNING: An error occured during configuration of the temperature sensor at serial interface ' + serialport + '. The temperature sensor cannot be used.\n' )
			self.warning ('An error occured during configuration of the temperature sensor at serial interface ' + serialport + '. The temperature sensor cannot be used.')


	########################################################################################################


	def get_UART_lock(self):
		'''
		temperaturesensor_MAXIM.get_UART_lock()
		
		Lock UART port for exclusive access (important if different threads / processes are trying to use the port). Make sure to release the lock after using the port (see temperaturesensor_MAXIM.release_UART_lock()!
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# wait until the serial port is unlocked:
		while self._UART_locked == True:
			time.sleep(0.01)
			
		# lock the port:
		self._UART_locked = True


	########################################################################################################


	def release_UART_lock(self):
		'''
		temperaturesensor_MAXIM.release_UART_lock()
		
		Release lock on UART port.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# release the lock:
		self._UART_locked = False

	
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
		

	def temperature(self,f,add_to_tempbuffer=True):
		"""
		temp,unit = temperaturesensor_MAXIM.temperature(f)
		
		Read out current temperaure value.
		
		INPUT:
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		add_to_tempbuffer (optional): flag to indicate if data get appended to temperature buffer (default=True)

		OUTPUT:
		temp: temperature value (float)
		unit: unit of temperature value (string)
		"""	

		temp = None;
		unit = '?';
		t = misc.now_UNIX()
		if not(hasattr(self,'_sensor')):
			self.warning( 'sensor is not initialised, could not read data.' )
		else:
			try:
				self.get_UART_lock()
				temp = self._sensor.get_temperature()
				self.release_UART_lock()
				unit = 'deg.C'
		
				# add data to peakbuffer
				if add_to_tempbuffer:
					self.tempbuffer_add(t,temp,unit)
			except:
				self.release_UART_lock()
				self.warning( 'could not read sensor!' )

		# write data to datafile
		if not ( f == 'nofile' ):
			# get timestamp

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
		
		misc.warnmessage ('[' + self.label() + '] ' + msg)


	########################################################################################################
	

	def tempbuffer_add(self,t,T,unit):
		"""
		temperaturesensor_MAXIM.tempbuffer_add(t,T,unit)
		
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
		timestamp = temperaturesensor_MAXIM.tempbuffer_get_timestamp()

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
		temperaturesensor_MAXIM.plot_tempbuffer()

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
		temperaturesensor_MAXIM.pressbuffer_clear()

		Clear the buffer of temperature readings

		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		# clear data buffer for TEMPERATURE values:

		if not(hasattr(self,'_sensor')):
			self.warning( 'sensor is not initialised, could not clear data buffer.' )
		else:
			self._tempbuffer_t = self._tempbuffer_t[[]]
			self._tempbuffer_T = self._tempbuffer_T[[]]
			self._tempbuffer_unit = ['x'] * 0 # empty list
			self._tempbuffer_lastupdate_timestamp = misc.now_UNIX()



	########################################################################################################
