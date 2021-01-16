# Code for the SRS RGA mass spec class
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
	import serial
	import time
	import struct
	import math
	import numpy
	import os
	from scipy.interpolate import interp1d
	from classes.misc	import misc
except ImportError as e:
	print (e)
	raise

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / rgams_SRS class is running on Python version < 3. Version 3.0 or newer is recommended!")

havedisplay = "DISPLAY" in os.environ
if havedisplay: # prepare plotting environment
	try:
		import matplotlib
		matplotlib.use('TkAgg')
		matplotlib.rcParams['legend.numpoints'] = 1
		matplotlib.rcParams['axes.formatter.useoffset'] = False
	except ImportError:
		misc.warnmessage ('Could not load and configure matplotlib, cannot set up display environment.')
		havedisplay = False
	except:
		misc.warnmessage ('Unexpected error while loading matplotlib, cannot set up display environment.')
		havedisplay = False

		# suppress mplDeprecation warning:
		## import warnings
		## import matplotlib.cbook
		## warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
		
	try:
		import matplotlib.pyplot as plt
	except ImportError:
		misc.warnmessage ('Could not load and configure pyplot, cannot set up display environment.')
		havedisplay = False
	except:
		misc.warnmessage ('Unexpected error while loading pyplot, cannot set up display environment.')
		havedisplay = False


class rgams_SRS:
	"""
	ruediPy class for SRS RGA-MS control.
	"""


	########################################################################################################


	def __init__( self , serialport , label='MS' , cem_hv = 1400 , tune_default_RI = [] , tune_default_RS = [] , max_buffer_points = 500 , fig_w = 10 , fig_h = 8 , peakbuffer_plot_min=0.5 , peakbuffer_plot_max = 2 , peakbuffer_plot_yscale = 'linear' , has_plot_window = True , has_external_plot_window = False):

		'''
		rgams_SRS.__init__( serialport , label='MS' , cem_hv = 1400 , tune_default_RI = [] , tune_default_RS = [] , max_buffer_points = 500 , fig_w = 10 , fig_h = 8 , peakbuffer_plot_min=0.5 , peakbuffer_plot_max = 2 )
		
		Initialize mass spectrometer (SRS RGA), configure serial port connection.
		
		INPUT:
		serialport: device name of the serial port, e.g. P = '/dev/ttyUSB4' or P = '/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2350938-if00-port0'
		label (optional): label / name of the RGAMS object (string). Default: label = 'MS'
		cem_hv (optional): default bias voltage to be used with the electron multiplier (CEM). Default value: cem_hv = 1400 V.
		tune_default_RI (optional): default RI parameter value in m/z tuning. Default value: tune_RI = []
		tune_default_RS (optional): default RS parameter value in m/z tuning. Default value: tune_RS = []
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches). 
		peakbuffer_plot_min, peakbuffer_plot_max (optional): limits of y-axis range in peakbuffer plot (default: peakbuffer_plot_min=0.5 , peakbuffer_plot_max = 2)
		peakbuffer_plot_yscale (optional) = y-axis scaling for peakbuffer plot (default: 'linear', use 'log' for log scaling)
		has_plot_window (optional): flag to choose if a plot window should be opened for the rgams_SRS object (default: has_plot_window = True)
		has_external_plot_window (optional) = flag to indicate if external plot window is used instead of the "built-in" window. If set to True, this will override the 'has_plot_window' flag (default: has_external_plot_window = False).

		OUTPUT:
		(none)
		'''

		try:
		
			# open and configure serial port for communication with SRS RGA (28'800 baud, 8 data bits, no parity, 2 stop bits
			# use exclusive access mode if possible (available with serial module version 3.3 and later)

			from pkg_resources import parse_version
			if parse_version(serial.__version__) >= parse_version('3.3') :
				# open port with exclusive access:
				ser = serial.Serial(
					port      = serialport,
					baudrate  = 28800,
					parity    = serial.PARITY_NONE,
					stopbits  = serial.STOPBITS_TWO,
					bytesize  = serial.EIGHTBITS,
					timeout   = 10.0,
					exclusive = True
				)

			else:
				# open port (can't ask for exclusive access):
				ser = serial.Serial(
					port     = serialport,
					baudrate = 28800,
					parity   = serial.PARITY_NONE,
					stopbits = serial.STOPBITS_TWO,
					bytesize = serial.EIGHTBITS,
					timeout  = 10.0
				)

			ser.flushOutput()	# make sure output is empty
			time.sleep(0.1)
			ser.flushInput()	# make sure input is empty
		
			self.ser = ser
			self._ser_locked = False
			
			# object name label:
			self._label = label
		
			# get ID / serial number of SRS RGA:
						
			sn = self.param_IO('ID?',1)
			sn = sn.split('.')
			self._serial_number = sn[1]
			
			# cem bias / high voltage:
			self._cem_hv = cem_hv

			# m/z tune defaults:
			self._tune_default_RI = tune_default_RI
			self._tune_default_RS = tune_default_RS

			# data buffer for PEAK values:
			self._peakbuffer_t = numpy.array([])
			self._peakbuffer_mz = numpy.array([])
			self._peakbuffer_intens = numpy.array([])
			self._peakbuffer_det = ['x'] * 0 # empty list
			self._peakbuffer_unit = ['x'] * 0 # empty list
			self._peakbuffer_max_len = max_buffer_points
			self._peakbuffer_lastupdate_timestamp = -1

			# y-axis range:
			self._peakbuffer_plot_min_y = peakbuffer_plot_min
			self._peakbuffer_plot_max_y = peakbuffer_plot_max

			# y-axis scaling for peakbuffer plot:
			self._peakbufferplot_yscale = peakbuffer_plot_yscale
			
			# mz values and colors (defaults):
			self._peakbufferplot_colors = [ (2,'darkgray') , (4,'c') , (13,'darkgray') , (14,'dimgray') , (15,'green') , (16,'lightcoral') , (28,'k') , (32,'r') , (40,'y') , (44,'b') , (84,'m') ] # default colors for the more common mz values

			# set up plotting environment
			if not has_external_plot_window:
				if misc.have_external_gui():
					self.warning( 'It looks like there is an external GUI. Configuring the MS with has_external_plot_window=True although no external plot window was requested!' )
					has_external_plot_window = True
			self._has_external_display = has_external_plot_window
			if self._has_external_display:
				has_plot_window = False # don't care with the built-in plotting, which will be dealt with externally
			self._has_display = has_plot_window # try opening a plot window
			if has_plot_window: # should have a plot window
				self._has_display = havedisplay # don't try opening a plot window if there is no plotting environment
			else: # no plot window
				self._has_display = False
		
			if self._has_display: # prepare plotting environment and figure

				# set up plotting environment
				self._fig = plt.figure(figsize=(fig_w,fig_h))
				# f.suptitle('SRS RGA DATA')
				t = 'SRS RGA'
				if self._label:
					t = t + ' (' + self._label + ')'
				self._fig.canvas.set_window_title(t)

				# set up upper panel for peak history plot:
				self._peakbuffer_ax = plt.subplot(2,1,1)
				self._peakbuffer_ax.set_title('PEAKBUFFER (' + self.label() + ')',loc="center")
				plt.xlabel('Time')
				plt.ylabel('Intensity')

				# add (empty) line to plot (will be updated with data later):
				self._peakbuffer_ax.plot( [], [] )
				self.set_peakbuffer_scale(self._peakbufferplot_yscale)

				# set up lower panel for scans:
				self._scan_ax = plt.subplot(2,1,2)
				self._scan_ax.set_title('SCAN (' + self.label() + ')',loc="center")
				plt.xlabel('mz')
				plt.ylabel('Intensity')

				# get some space in between panels to avoid overlapping labels / titles
				self._fig.tight_layout(pad=4.0)

				self._figwindow_is_shown = False
				plt.ion()		
			
			print( 'Successfully configured SRS RGA MS with serial number ' + str(self._serial_number) + ' on ' + serialport )


		except serial.SerialException as e:
			misc.warnmessage ('Could not establish connection to SRS RGA:' + str(e) )
			sys.exit(1)

		except:
			self.warning('Unexpected error during initialisation of SRS RGA:' + str(sys.exc_info()[0]) )
			sys.exit(1)

	########################################################################################################
	

	def label(self):
		"""
		l = rgams_SRS.label()
		
		Return label / name of the RGAMS object.
		
		INPUT:
		(none)
		
		OUTPUT:
		l: label / name (string)
		"""
		
		return self._label

	
	########################################################################################################
	

	def warning(self,msg):
		'''
		rgams_SRS.warning(msg)
		
		Issue warning about issues related to operation of MS.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.warnmessage ('[' + self.label() + '] ' + msg)

	
	########################################################################################################

	
	def log(self,msg):
		'''
		rgams_SRS.log(msg)
		
		Issue log message related to operation of MS.
		
		INPUT:
		msg: log message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.logmessage ('[' + self.label() + '] ' + msg)

	
	########################################################################################################

	
	def get_peakbuffer(self):
		'''
		x = rgams_SRS.get_peakbuffer(self)
		
		Return peakbuffer data (for use with external modules)

		INPUT:
		(none)
		
		OUTPUT:
		x: peakbuffer data, struct with the following fields:
			x.t: time values (float)
			x.intens: PEAK intensities (float)
			x.mz: m/z ratio (int)
			x.unit: unit of the PEAK values (string)
			x.det: detector used for PEAK rading (string)
		'''

		class peakbuffer:
			def __init__(self,t,intens,mz,unit,det):
				self.t      = t
				self.intens = intens
				self.mz     = mz
				self.unit   = unit
				self.det    = det
		
		x = peakbuffer(self._peakbuffer_t, self._peakbuffer_intens, self._peakbuffer_mz, self._peakbuffer_unit, self._peakbuffer_det)
		return(x)


	########################################################################################################

	
	def get_peakbuffer_scale(self):
		'''
		s = rgams_SRS.get_peakbuffer_scale(self)
		
		Get scale of y-axis in peakbuffer plot (linear or log).

		INPUT:
		(none)
		
		OUTPUT:
		s: scale (string, either 'linear' or 'log', default: scale = 'linear')
		'''
		
		if self._peakbufferplot_yscale.upper() == 'LOG':
			return 'log'
		else:
			return 'linear'


	########################################################################################################

	
	def set_peakbuffer_scale(self,scale='linear'):
		'''
		rgams_SRS.set_peakbuffer_scale(scale)
		
		Set scale of y-axis in peakbuffer plot (linear or log).

		INPUT:
		scale: scale (string, either 'linear' or 'log, default: scale = 'linear')
		
		OUTPUT:
		(none)
		'''
		
		# change scale
		scale = scale.upper()
		if scale == 'LINEAR':
			self._peakbufferplot_yscale = 'linear'
		elif scale == 'LOG':
			self._peakbufferplot_yscale = 'log'
		else:
			self.warning('Unknown peakbuffer sccale: ' + scale )

		if self._has_display:
			# if plot is not handled by external GUI:
			self._peakbuffer_ax.set_yscale(self._peakbufferplot_yscale)

			from matplotlib.ticker import FuncFormatter
			yformatter = FuncFormatter(lambda y, _: '{:.1%}'.format(y))
			self._peakbuffer_ax.yaxis.set_major_formatter(yformatter)

	
	########################################################################################################
	

	def get_serial_lock(self):
		'''
		rgams_SRS._get_serial_lock()
		
		Lock serial port for exclusive access (important if different threads / processes are trying to use the port). Make sure to release the lock after using the port (see rgams_SRS._release_serial_lock()!
		
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
		rgams_SRS._release_serial_lock()
		
		Release lock on serial port.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# release the lock:
		self._ser_locked = False


	
	########################################################################################################

	

	def param_IO(self,cmd,ansreq,timeout=10,wait_between_bytes=0.02):
		'''
		ans = rgams_SRS.param_IO(cmd,ansreq)
		
		Set / read parameter value of the SRS RGA.

		INPUT:
		cmd: command string that is sent to RGA (see RGA manual for commands and syntax)
		ansreq: flag indicating if answer from RGA is expected:
			ansreq = 1: answer expected, check for answer
			ansreq = 0: no answer expected, don't check for answer
		timeout (optional): max. wait time for answer from RGA (seconds), default: timeout = 10 seconds
		wait_between_bytes (optional): wait time between reads of single response bytes (seconds), default = 0.02 seconds. If reading answer from RGA, it may be required to wait a short time between reading each single byte. If the data is coming too slowly, the data reading might empty the input buffer before all the data is transferred for the RGA to the buffer, and the code would then assume it is done with reading all the data. Adding a small wait time in between the single reads of each byte helps to avoid this problem.

		OUTPUT:
		ans: answer / result returned from RGA
		'''

		# lock the serial port
		self.get_serial_lock()
	
		# check if serial buffer (input) is empty (just in case, will be useful to catch errors):
		if self.ser.inWaiting() > 0:
			self.warning('DEBUGGING INFO: serial buffer not empty before executing command = ' + cmd + '.')

		# send command to serial port:
		self.ser.write((cmd + '\r\n').encode('utf-8'))
		
		if ansreq:

			# wait for response
			t = 0
			dt = 0.1
			doWait = 1
			while doWait:
				if self.ser.inWaiting() == 0: # nothing in the buffer yet, wait
					time.sleep(dt)
					t = t + dt
					if t > timeout: # give up waiting
						doWait = 0
						self.warning('could not determine parameter value or status (no response from RGA, command: ' + cmd + ')')
						ans = -1
				else:
					doWait = 0
					ans = ''
		
			# read back result:
			if ans == -1:
				self.warning('Execution of ' + cmd + ' did not produce a result (or took too long)!')
			else:
				while self.ser.inWaiting() > 0: # while there's something in the buffer...
					ans = ans + self.ser.read().decode('utf-8') # read each byte
					if wait_between_bytes > 0.0:
						time.sleep(wait_between_bytes) # allow some time before quering for the next byte

				ans = ans.rstrip('\r\n') # remove newline characters at end
					
		else: # check if serial buffer is empty (will be useful to catch errors):
			ans = None
			if self.ser.inWaiting() > 0:
				self.warning('DEBUGGING INFO: serial buffer not empty after executing command = ' + cmd +'. First byte in buffer: ' + self.ser.read().decode('utf-8') )

		# release the lock on the serial port
		self.release_serial_lock()

		# return the result:
		if ans is not None:
			return ans

			
	
	########################################################################################################


	
	def electron_energy_min(self):
		'''
		val = rgams_SRS.electron_energy_min()
		
		Return lowest electron energy value supported by the MS.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: min. supported mz value (int)
		'''

		# lowest value for SRS RGA:
		return 25.0

			
	
	########################################################################################################


	
	def electron_energy_max(self):
		'''
		val = rgams_SRS.electron_energy_max()
		
		Return highest electron energy value supported by the MS.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: max. supported mz value (int)
		'''

		# highest value for SRS RGA:
		return 105.0

			
	
	########################################################################################################


	
	def set_electron_energy(self,val):
		'''
		rgams_SRS.set_electron_energy(val)
		
		Set electron energy of the ionizer.
		
		INPUT:
		val: electron energy in eV
		
		OUTPUT:
		(none)
		'''
		
		maxval = self.electron_energy_max()
		minval = self.electron_energy_min()
		if val > maxval:
			self.warning ('EE parameter cannot be higher than ' + str(minval) + '. Using EE = ' + str(maxval) + '...')
			val = maxval
		if val < minval:
			self.warning ('EE parameter cannot be less than ' + str(minval) + '. Using EE = ' + str(minval) + '...')
			val = minval

		# send command to serial port:
		self.param_IO('EE' + str(val),1)

	
	########################################################################################################
	

	def get_default_RI(self):
		'''
		val = rgams_SRS.get_default_RI()
		
		Return default RI value.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: default RI value
		'''

		ans = self._tune_default_RI
		if not ans:
			self.warning ('Default RI value is not set!')
		return ans

	
	########################################################################################################
	

	def get_default_RS(self):
		'''
		val = rgams_SRS.get_default_RS()
		
		Return default RS value.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: default RS value
		'''
		
		ans = self._tune_default_RS
		if not ans:
			self.warning ('Default RS value is not set!')
		return ans


	########################################################################################################
	

	def get_electron_energy(self):
		'''
		val = rgams_SRS.get_electron_energy()
		
		Return electron energy of the ionizer (in eV).
		
		INPUT:
		(none)
		
		OUTPUT:
		val: electron energy in eV
		'''
		
		# send command to serial port:
		ans = float(self.param_IO('EE?',1))
		return ans


	########################################################################################################
	

	def set_multiplier_hv(self,val):
		'''
		rgams_SRS.set_multiplier_hv(val)
		
		Set electron multiplier (CEM) high voltage (bias voltage).
		
		INPUT:
		val: voltage
		
		OUTPUT:
		(none)
		'''
		
		# check if CEM option is installed:
		if self.has_multiplier():
			# send command to serial port:
			self.param_IO(cmd='HV' + str(val),ansreq=1) # note that setting the HV value seems to be slow, and the RGA response to the serial buffer may be slow. Therefore wait_between_bytes > 0.0

		else:
			self.warning ('Cannot set multiplier (CEM) high voltage, because CEM option is not installed.')


	########################################################################################################
	

	def get_multiplier_hv(self):
		'''
		val = rgams_SRS.get_multiplier_hv()
		
		Return electron multiplier (CEM) high voltage (bias voltage).
		
		INPUT:
		(none)
		
		OUTPUT:
		val: voltage
		'''
		
		# check if CEM option is installed:
		if self.has_multiplier():
			# send command to serial port:
			ans = float(self.param_IO('HV?',1))
		else:
			self.warning ('Cannot get multiplier (CEM) high voltage, because CEM option is not installed.')
			ans = None

		return ans
		
		
	########################################################################################################
	

	def get_multiplier_default_hv(self):
		'''
		val = rgams_SRS.get_multiplier_default_hv()
		
		Return default value to be used for electron multiplier (CEM) high voltage (bias voltage).
		NOTE: the value returned is NOT the value stored in the memory of the RGA head. This function is just a wrapper that returns the default high voltage value set in the RGA object (e.g., during initialisation of the object).
		
		INPUT:
		(none)
		
		OUTPUT:
		val: voltage
		'''

		return self._cem_hv

	
	########################################################################################################
	

	def set_electron_emission(self,val):
		'''
		rgams_SRS.set_electron_emission(val)
		
		Set electron emission current.
		
		INPUT:
		val: electron emission current in mA (0 ... 3.5 mA)
		
		OUTPUT:
		(none)
		'''
			
		# send command to serial port:
		self.param_IO('FL' + str(val),1)

	
	########################################################################################################
	

	def get_electron_emission(self):
		'''
		val = rgams_SRS.get_electron_emission()
		
		Return electron emission current (in mA)
		
		INPUT:
		(none)
		
		OUTPUT:
		val: electron emission current in mA (float)
		'''
				
		# send command to serial port:
		ans = float(self.param_IO('FL?',1))
		return ans

	
	########################################################################################################
	


	def is_filament_on(self):
		'''
		val = rgams_SRS.is_filament_on()
		
		Check is filamen is turned on or off.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: on / off state (Boolean)
		'''

		if self.get_electron_emission() == 0.0:
			return False
		else:
			return True



	########################################################################################################



	def filament_on(self):
		'''
		rgams_SRS.filament_on()
		
		Turn on filament current at default current value.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''
				
		# send command to serial port:
		self.param_IO('FL*',1)

	
	########################################################################################################
	

	def filament_off(self):
		'''
		rgams_SRS.filament_off()
		
		Turn off filament current.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''
		
		# turn off filament (set current to zero)
		self.set_electron_emission(0)

	
	########################################################################################################
	
	
	def supported_gate_times(self):
		'''
		g = rgams_SRS.supported_gate_times()
		
		Return the gate times that are supported by the hardware (estimated values if MS has electron multiplier installed.
		
		INPUT:
		(none)
		
		OUTPUT:
		g: supported gate times in seconds (array)
		
		NOTE:
		Experiment gave the following gate times vs NF parameter values:
		
		  NF	gate (seconds)
		  0	2.4
		  1	1.21
		  2	0.48
		  3	0.25
		  4	0.163
		  5	0.060
		  6	0.043
		  7	0.025
		'''

		return [ 2.4 , 1.2 , 0.6 , 0.3 , 0.15 , 0.08 , 0.04 , 0.02 ]

	
	########################################################################################################
	
	
	def has_multiplier(self):
		'''
		val = rgams_SRS.has_multiplier()
		
		Check if MS has electron multiplier installed.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: result flag, val = 0 --> MS has no multiplier, val <> 0: MS has multiplier
		'''

		if hasattr(self, '_hasmulti') == 0: # never asked for multiplier before
			u = self.param_IO('MO?',1)
			if u:
				self._hasmulti = 1
			else:
				self._hasmulti = 0
		return self._hasmulti

	
	########################################################################################################
	

	def mz_max(self):
		'''
		val = rgams_SRS.mz_max()
		
		Determine highest mz value supported by the MS.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: max. supported mz value (int)
		'''

		if hasattr(self, '_mzmax') == 0: # never asked for mz_max before
			x = self.param_IO('MF?',1) # get current MF value
			self.param_IO('MF*',0) # set MF to default value, which equals M_MAX
			self._mzmax = int ( self.param_IO('MF?',1) ) # read back M_MAX value
			self.param_IO('MF' + x,0) # set back to previous MF value
		return self._mzmax


	########################################################################################################
	

	def mz_min(self):
		'''
		val = rgams_SRS.mz_min()
		
		Determine lowest mz value supported by the MS.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: min. supported mz value (int)
		'''

		# lowest m/z for SRS RGA is m/z=1:
		return 1

	
	########################################################################################################
	

	def set_detector(self,det):
		'''
		rgams_SRS.set_detector(det)
		
		Set current detetector used by the MS (direct the ion beam to the Faraday or electron multiplier detector).
		NOTE: To activate the electron multiplier (CEM), the default high voltage (bias voltage) as returned by self.get_multi_default_hv() is used (this is NOT necessarily the same as the default value stored in the RGA head).
		
		INPUT:
		det: detecor (string):
			det='F' for Faraday
			det='M' for electron multiplier
		
		OUTPUT:
		(none)
		'''
		
		# send command to serial port:
		if det == 'F':
			self.param_IO('HV0',1)

		elif det == 'M':
			if self.has_multiplier():
				# self.param_IO('HV*',1)  <--- this uses the factory default value (HV = 1400 V)
				self.set_multiplier_hv(self.get_multiplier_default_hv())

			else:
				self.warning ('RGA has no electron multiplier installed!')
		else:
			self.warning ('Unknown detector ' + det)

	
	########################################################################################################
	

	def get_detector(self):
		'''
		det = rgams_SRS.get_detector()
		
		Return current detector (Faraday or electron multiplier)
		
		INPUT:
		(none)
		
		OUTPUT:
		det: detecor (string):
			det='F' for Faraday
			det='M' for electron Multiplier
		'''
		
		if not self.has_multiplier(): # there is no Multiplier installed
			det = 'F'
		else:
			hv = self.param_IO('HV?',1) # send command to serial port
			try:
				hv = float(hv)
				if hv == 0:
					det = 'F'
				else:
					det = 'M'
			except ValueError:
				det = '?'
				self.warning ('Could not determine electron multiplier high voltage (could not convert string to float). RGA-MS returned HV = ' + hv )
			except:
				self.warning ('Unexpected error. Could not determine electron multiplier HV.' )
		return det

	
	########################################################################################################
	

	def get_noise_floor(self):
		'''
		val = rgams_SRS.get_noise_floor()
		
		Get noise floor (NF) parameter for RGA measurements (noise floor controls gate time, i.e., noise vs. measurement speed).
				
		INPUT:
		(none)
		
		OUTPUT:
		val: NF noise floor parameter value, 0...7 (integer)
		'''

		if hasattr(self, '_noisefloor') == 0: # never asked for noisefloor before
			self._noisefloor = float( self.param_IO('NF?',1) ) # get current NF value
			
		return self._noisefloor

	
	########################################################################################################
	


	def set_noise_floor(self,NF):
		'''
		val = rgams_SRS.set_noise_floor()
		
		Set noise floor (NF) parameter for RGA measurements (noise floor controls gate time, i.e., noise vs. measurement speed).
				
		INPUT:
		NF: noise floor parameter value, 0...7 (integer)
		
		OUTPUT:
		(none)
		'''
		
		NF = int(NF) # make sure NF is an integer value
		if NF > 7:
			self.warning ('NF parameter must be 7 or less. Using NF = 7...')
			NF = 7
		elif NF < 0:
			self.warning ('NF parameter must be 0 or higher. Using NF = 0...')
			NF = 0
		
		if NF != self.get_noise_floor(): # only change NF setting if necessary
			self.param_IO('NF' + str(NF),0)
			self._noisefloor = NF # remember new NF value

	
	########################################################################################################
	

	def set_gate_time(self,gate):
		'''
		val = rgams_SRS.set_gate_time()
		
		Set noise floor (NF) parameter for RGA measurements according to desired gate time (by choosing the best-match NF value).
				
		INPUT:
		gate: gate time in (fractional) seconds
		
		OUTPUT:
		(none)

		NOTE (1):
		FROM THE SRS RGA MANUAL:
		Single mass measurements are commonly performed in sets
		where several different masses are monitored sequencially
		and in a merry-go-round fashion.
		For best accuracy of results, it is best to perform the consecutive
		mass measurements in a set with the same type of detector
		and at the same noise floor (NF) setting.
		Fixed detector settings eliminate settling time problems
		in the electrometer and in the CDEM HV power supply.
		
		NOTE (2):
		see self.supported_gate_times() for more information on gate times supported by the RGA.
		Experiment gave the following gate times vs NF parameter values:
		
		  NF	gate (seconds)
		  0	2.4
		  1	1.21
		  2	0.48
		  3	0.25
		  4	0.163
		  5	0.060
		  6	0.043
		  7	0.025
		'''
		
		gt = numpy.array( self.supported_gate_times() )
		NF = (numpy.abs(gt-gate)).argmin() # index to closest gate time
		if gate > gt.max():
			self.warning('gate time cannot be more than ' + str(gt.max()) +'s! Using gate = ' + str(gt.max()) +'s...')
		elif gate < gt.min():
			self.warning('gate time cannot be less than ' + str(gt.min()) +'s! Using gate = ' + str(gt.min()) +'s...')
			
		self.set_noise_floor(NF)

	
	########################################################################################################
	

	def peakbuffer_add(self,t,mz,intens,det,unit):
		"""
		rgams_SRS.peakbuffer_add(t,mz,intens,unit)
		
		Add data to PEAKS data buffer
				
		INPUT:
		t: epoch time
		mz: mz values
		intens: intensity value
		det: detector (char/string)
		unit: unit of intensity value (char/string)
		
		OUTPUT:
		(none)
		"""

		self._peakbuffer_t = numpy.append( self._peakbuffer_t , t )
		self._peakbuffer_mz = numpy.append( self._peakbuffer_mz , mz )
		self._peakbuffer_intens = numpy.append( self._peakbuffer_intens , intens )
		self._peakbuffer_det.append( det )
		self._peakbuffer_unit.append( unit )

		N = self._peakbuffer_max_len
		
		if self._peakbuffer_t.shape[0] > N:
			self._peakbuffer_t      = self._peakbuffer_t[-N:]
			self._peakbuffer_mz     = self._peakbuffer_mz[-N:]
			self._peakbuffer_intens = self._peakbuffer_intens[-N:]
			self._peakbuffer_det    = self._peakbuffer_det[-N:]
			self._peakbuffer_unit   = self._peakbuffer_unit[-N:]
			
		self._peakbuffer_lastupdate_timestamp = misc.now_UNIX()



	########################################################################################################



	def peakbuffer_clear(self):
		"""
		rgams_SRS.peakbuffer_clear()

		Clear data in PEAKS data buffer

		INPUT:
		(none)

		OUTPUT:
		(none)
		"""

		self._peakbuffer_t      = self._peakbuffer_t[[]]
		self._peakbuffer_mz     = self._peakbuffer_mz[[]]
		self._peakbuffer_intens = self._peakbuffer_intens[[]]
		self._peakbuffer_det    = ['x'] * 0 # empty list
		self._peakbuffer_unit   = ['x'] * 0 # empty list
		self._peakbuffer_lastupdate_timestamp = misc.now_UNIX()


########################################################################################################



	def peakbuffer_set_length(self,N):
		"""
		rgams_SRS.peakbuffer_set_length(N)

		Set max. length of peakbuffer

		INPUT:
		N: number of PEAK values

		OUTPUT:
		(none)
		"""

		self._peakbuffer_max_len = N



########################################################################################################



	def peakbuffer_get_timestamp(self):
		"""
		timestamp = rgams_SRS.peakbuffer_get_timestamp()

		Get time stamp of last update to peakbuffer data
		
		INPUT:
		(none)

		OUTPUT:
		timestamp: UNIX time of last update
		"""

		return self._peakbuffer_lastupdate_timestamp



########################################################################################################



	def peak(self,mz,gate,f,add_to_peakbuffer=True,peaktype=None):
		'''
		val,unit = rgams_SRS.peak(mz,gate,f,add_to_peakbuffer=True,peaktype=None)
		
		Read out detector signal at single mass (m/z value).
		
		INPUT:
		mz: m/z value (integer)
		gate: gate time (seconds) NOTE: gate time can be longer than the max. gate time supported by the hardware (2.4 seconds). If so, the multiple peak readings will be averaged to achieve the requested gate time.
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		add_to_peakbuffer (optional): flag to choose if peak value is added to peakbuffer (default: add_to_peakbuffer=True)
		peaktype (optional): string to indicate the "type" of the PEAK reading (default: type=None). Specifying type will add the type string the the PEAK identifier in the data file in order to tell the processing tool(s) to use the PEAK_xyz reading for a specific purpose. Example: type='DECONV' will change the PEAK identifier to PEAK_DECONV, which will be used for deconvolution of mass spectrometric overlaps.
		
		OUTPUT:
		val: signal intensity (float)
		unit: unit (string)
		
		NOTE FROM THE SRS RGA MANUAL:
		Single mass measurements are commonly performed in sets
		where several different masses are monitored sequencially
		and in a merry-go-round fashion.
		For best accuracy of results, it is best to perform the consecutive
		mass measurements in a set with the same type of detector
		and at the same noise floor (NF) setting.
		Fixed detector settings eliminate settling time problems
		in the electrometer and in the CDEM's HV power supply.
		'''
		
		# check for range of input values:
		mz = int(mz)

		# get timestamp
		t = misc.now_UNIX()
		
		if mz < self.mz_min():
			self.warning ('mz value must be ' + str(self.mz_min()) + ' or higher! Skipping peak measurement...')
			val = '-1'
			unit = '(none)'
			
		elif mz > self.mz_max():
			self.warning ('mz value must be ' + str(self.mz_max()) + ' or less! Skipping peak measurement...')
			val = '-1'
			unit = '(none)'
			
		else: # proceed with measurement

			# deal with gate times longer than 2.4 seconds (max. allowed with SRS-RGA):
			v = 0.0;
			if gate > max(self.supported_gate_times()):
				N = int(round(gate/max(self.supported_gate_times())))
				gt = max(self.supported_gate_times())
			else:
				N = 1
				gt = gate
			
			# configure RGA (gate time):
			self.set_gate_time(gt)

			# lock serial port, make sure serial port buffers are empty:
			self.get_serial_lock() # wait until serial port is available, then lock it for access
			self.ser.flushOutput()
			self.ser.flushInput()

			for k in range(N):
				
				# send command to RGA:
				self.ser.write(('MR' + str(mz) + '\r\n').encode('utf-8'))
				
				# read back data:
				u = self.ser.read(4) # this will wait until all 4 bytes are received
				
				# make sure the serial in buffer is empty:
				time.sleep(0.02) # wait a bit to make sure that serial buffers are up to date (although there should be no more than 4 data bytes in the input buffer, which are all read out by the command above
				while self.ser.inWaiting() > 0:
					self.warning('DEBUGGING INFO: serial input buffer not empty after PEAK reading!')
					self.ser.flushInput()
					time.sleep(0.02)
	
				# parse result:
				u = struct.unpack('<i',u)[0] # unpack 4-byte data value
				
				v = v + u
			
			# release lock on serial port:
			self.release_serial_lock()

			v = v/N
			val = v * 1E-16 # multiply by 1E-16 to convert to Amperes
			unit = 'A'
					
		det = self.get_detector()
		
		if not ( f == 'nofile' ):
			f.write_peak('RGA_SRS',self.label(),mz,val,unit,det,gate,t,peaktype)
		
		# add data to peakbuffer
		if add_to_peakbuffer:
			self.peakbuffer_add(t,mz,val,det,unit)
			
		return val,unit
		
		
	########################################################################################################
	

	def zero(self,mz,mz_offset,gate,f,zerotype=None):
		'''
		val,unit = rgams_SRS.zero(mz,mz_offset,gate,f,zerotype=None)
		
		Read out detector signal at single mass with relative offset to given m/z value (this is useful to determine the baseline near a peak at a given m/z value), see rgams_SRS.peak())
		The detector signal is read at mz+mz_offset
		
		INPUT:
		mz: m/z value (integer)
		mz_offset: offset relative m/z value (integer).
		gate: gate time (seconds) NOTE: gate time can be longer than the max. gate time supported by the hardware (2.4 seconds). If so, the multiple zero readings will be averaged to achieve the requested gate time.
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		zerotype (optional): string to indicate the "type" of the ZERO reading (default: type=None). See 'peaktype' argument for self.peak(...).
		
		OUTPUT:
		val: signal intensity (float)
		unit: unit (string)
		
		NOTE FROM THE SRS RGA MANUAL:
		Single mass measurements are commonly performed in sets
		where several different masses are monitored sequencially
		and in a merry-go-round fashion.
		For best accuracy of results, it is best to perform the consecutive
		mass measurements in a set with the same type of detector
		and at the same noise floor (NF) setting.
		Fixed detector settings eliminate settling time problems
		in the electrometer and in the CDEM's HV power supply.
		'''
		
		# check for range of input values:
		mz = int(mz)
		mz_offset = int (mz_offset)

		# get timestamp
		t = misc.now_UNIX()
		
		if mz+mz_offset < 1:
			self.warning ('mz+mz_offset must be positive! Skipping zero measurement...')
			val = '-1'
			unit = '(none)'
			
		elif mz+mz_offset > self.mz_max():
			self.warning ('mz+mz_offset value must be ' + self.mz_max() + ' or less! Skipping zero measurement...')
			val = '-1'
			unit = '(none)'
			
		else: # proceed with measurement
		
			# deal with gate times longer than 2.4 seconds (max. allowed with SRS-RGA):
			v = 0.0;
			if gate > max(self.supported_gate_times()):
				N = int(round(gate/max(self.supported_gate_times())))
				gt = max(self.supported_gate_times())
			else:
				N = 1
				gt = gate
			# configure RGA (gate time):
			self.set_gate_time(gt)

			# lock serial port, make sure serial port buffers are empty:
			self.get_serial_lock() # wait until serial port is available, then lock it for access
			self.ser.flushOutput()
			self.ser.flushInput()

			for k in range(N):

				# send command to RGA:
				self.ser.write(('MR' + str(mz+mz_offset) + '\r\n').encode('utf-8'))

				# wait a bit to make sure that serial command is sent
				time.sleep(0.02)

				# read back data:
				u = self.ser.read(4)

				# wait a bit to make sure that serial buffers are up to date
				time.sleep(0.02)

				# make sure the serial in buffer is empty:
				while self.ser.inWaiting() > 0:
					self.warning('DEBUGGING INFO: serial input buffer not empty after ZERO reading!')
					self.ser.flushInput()
					time.sleep(0.02)

				# parse result:
				u = struct.unpack('<i',u)[0] # unpack 4-byte data value
				
				v = v + u

			# release lock on serial port:
			self.release_serial_lock()
			
			v = v/N
			val = v * 1E-16 # multiply by 1E-16 to convert to Amperes
			unit = 'A'

		if not ( f == 'nofile' ):
			f.write_zero('RGA_SRS',self.label(),mz,mz_offset,val,unit,self.get_detector(),gate,t,zerotype)

		return val,unit


	########################################################################################################


	def scan(self,low,high,step,gate,f):
		'''
		M,Y,unit = rgams_SRS.scan(low,high,step,gate,f)

		Analog scan

		INPUT:
		low: low m/z value (integer or decimal)
		high: high m/z value (integer or decimal)
		step: scan resolution (number of mass increment steps per amu)
		   step = integer number (10...25) --> use given number (high number equals small mass increments between steps)
		   step = '*' use default value (step = 10)
		gate: gate time (seconds)
		f: file object or 'nofile':
			if f is a DATAFILE object, the scan data is written to the current data file
			if f = 'nofile' (string), the scan data is not written to a datafile

		OUTPUT:
		M: mass values (mz, in amu)
		Y: signal intensity values (float)
		unit: unit of Y (string)
		'''

		# check for range of input values:
		llow  = low
		hhigh = high
		low   = math.floor(low)
		high  = math.ceil(high)
		step  = int(step)
		if step < 10:
			self.warning ('Scan step must be 10 or higher! Using step = 10...')
			step = 10
		if step > 25:
			self.warning ('Scan step must be 25 or less! Using step = 25...')
			step = 25
		if low < 0:
			self.warning ('Scan must start at m/z=0 or higher! Starting at m/z=0...')
			low = 0
		if high > self.mz_max():
			self.warning ('Scan must end at m/z=' + self.mz_max() + ' or lower! Ending at m/z= ' + self.mz_max() + '...')
			low = self.mz_max()
		if low >= high:
			self.warning ('Scan m/z value at start must be lower than at end. Swapping values...')
			x = low;
			low = high;
			high = x;

		# configure RGA (gate time):
		self.set_gate_time(gate)

		# configure scan:
		L = int(self.param_IO('MI?',1))
		H = int(self.param_IO('MF?',1))
		if high >= L:	# setting MF lower than current MI may fail
			self.param_IO('MF' + str(high),0) # high end mz value
			self.param_IO('MI' + str(low),0) # low end mz value
		else: # set MI first 
			self.param_IO('MI' + str(low),0) # low end mz value
			self.param_IO('MF' + str(high),0) # high end mz value
		self.param_IO('SA' + str(step),0) # number of steps per amu

		N = int(self.param_IO('AP?',1)) # number of data points in the scan

		# wait until serial port is available, then lock it for access
		self.get_serial_lock()

		# start the scan:
		self.ser.write('SC1\r\n'.encode('utf-8'))

		# get time stamp before scan
		t1 = misc.now_UNIX()

		# read back result from RGA:
		Y = [] # init empty list

		k = 0
		while ( k < N+1 ): # read data points. Note: after scanning, the RGA also measures the total pressure and returns this as an extra data point, giving N+1 data points in total. All N+1 data points need to be read in order to empty the data buffer.

			# wait for data in buffer:
			t = 0
			dt = 0.1
			doWait = 1
			while doWait > 0:
				if self.ser.inWaiting() == 0: # wait
					time.sleep(dt)
					t = t + dt
					if t > 10: # give up waiting
						doWait = -1
				else:
					doWait = 0

			# read back result:
			if doWait == -1:
				self.warning('RGA did not produce scan result (or took too long)!')
			else:
				u = self.ser.read(4)

				if k < N: # if this was not the final data point (total pressure)
					u = struct.unpack('<i',u)[0] # unpack 4-byte data value
					u = u * 1E-16 # divide by 1E-16 to convert to Amperes
					Y.append(u) # append value to list 'ans'

				# prepare for next value:
				k = k + 1

		# release lock on serial port
		self.release_serial_lock()

		# get time stamp after scan
		t2 = misc.now_UNIX()

		# determine "mean" timestamp
		t = (t1 + t2) / 2.0

		# determine scan mz values:
		low = float(low)
		high = float(high)
		M = [low + x*(high-low)/N for x in range(N)]
		unit = 'A'

		# discard data that are out of the desired mz range:
		Y = [ Y[i] for i in range(len(M)) if (M[i] >= llow) & (M[i] <= hhigh) ]
		M = [ m for m in M if (m >= llow) & (m <= hhigh) ]

		# write to data file:
		if not ( f == 'nofile' ):
			det = self.get_detector()
			f.write_scan('RGA_SRS',self.label(),M,Y,unit,det,gate,t)

		return M,Y,unit


	########################################################################################################
	

	def ionizer_degas(self,duration):
		'''
		val = rgams_SRS.ionizer_degas(duration)
		
		Run the ionizer degas procedure (see SRS RGA manual). Only run this with sufficiently good vacuum!
						
		INPUT:
		duration: degas time in minutes (0...20 / integer)
		
		OUTPUT:
		(none)
		'''
		
		duration = int(duration) # make sure it's an integer
		
		if duration > 20:
			self.warning('Degas time must not be longer than 20 minutes. Using duration = 20 min...')
		
		if duration < 0:
			self.warning('Degas time must be positive. Skipping degas procedure...')
		
		else:
			if duration > 0:
				self.log('Starting degas procedure...')

				# wait until serial port is available, then lock it for access
				self.get_serial_lock()

				# send degassing command:
				cmd = 'DG'+str(duration)+'\r\n'
				self.ser.write(cmd.encode('utf-8'))
			
				self.log('...degas procedure running...')

				# wait for response from degassing procedure:
				t = 0
				dt = 1
				doWait = 1
				while doWait > 0:
					if self.ser.inWaiting() == 0: # wait
						time.sleep(dt)
						t = t + dt
						if t > duration*60 + 10: # give up waiting
							self.warning('Degassing taking longer than expected!')
					else:
						doWait = 0

				# read back result:
				u = self.ser.read(1)
				if u == b'0':
					self.log('...degassing completed without error.')
				else:
					self.warning ('Degassing completed with error byte: ' + str(u) )

				# release lock on serial port
				self.release_serial_lock()



	########################################################################################################


	
	def calibrate_electrometer(self):
		'''
		val = rgams_SRS.calibrate_electrometer()
		
		Calibrate the electrometer I-V response curve (lookup table). See also the "CL" command in the SRS RGA manual.
				
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# execute the CL command:
		self.param_IO('CL',1,timeout=75) 



	########################################################################################################

	

	def calibrate_all(self):
		'''
		val = rgams_SRS.calibrate_all()
		
		Calibrate the internal coefficients for compensation of baseline offset and peak positions. This will zero the baseline for all noise-floor (NF) and detector combinations. See also the "CA" command in the SRS RGA manual.
				
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		DET = self.get_detector() # get current detector
		NF  = self.get_noise_floor() # get current noise floor setting

		# start with zeroing the noise floor for the Faraday detector
		self.set_detector('F')
		for nf in range(0,8):
			self.set_noise_floor(nf)
			self.param_IO('CA',1)

		# calibrate multiplier coefficients
		if self.has_multiplier():
			self.set_detector('M')
			for nf in range(0,8):
				self.set_noise_floor(nf)
				self.param_IO('CA',1) 
			self.set_detector(DET) # set detector back to initial setting
		self.set_noise_floor(NF) # set noise floor back to initial setting


########################################################################################################


	def tune_peak_position(self,peaks,max_iter=10,max_delta_mz=0.05,use_defaults=False,resolution=25):
		'''
		rgams_SRS.tune_peak_position(mz,gate,det,max_iter=10,max_delta_mz=0.05,use_defaults=False,resolution=25)

		Automatically adjust peak positions in mass spectrum to make sure peaks show up at the correct mz values. This is done by scanning peaks at different mz values, and determining their offset in the mz spectrum. The mass spectromter parameters are then adjusted to minimize the mz offsets (parameters RI and RF, which define the peak positions at mz=0 and mz=128). The procedure start with the currently set RI and RS values (if use_defaults = False) or the default values (if they are set and use_defaults = True). This needs at least two distinct peak mz values, one at a low and one at a high mz value. The procedure is repeated until either the peak position offsets at mz=0 and mz=128 are less than max_delta_mz or the number of iterations has reached max_iter.

		INPUT:
		peaks: list of (mz,width,gate,detector) tuples, where peaks should be scanned and tuned
			mz = mz value of peak (center of the scan)
			width = width of the peak (relative to center mz value)
			gate: gate time to be used for the scan
			detector: detector to be used for the scan ('F' or 'M')
		max_iter (optional): max. number of repetitions of the tune procedure
		maxdelta_mz (optional): tolerance of mz offset at mz=0 and mz=128. If the absolute offsets at mz=0 and mz=128 after tuning are less than maxdelta_z after tuning, the tuning procedure is stopped.
		use_defaults: flag to set if default RI and RS values are used to start the tuning procedure. Default value: use_defaults = False
		resolution: m/z resolution used for the scans (10...25 points per amu). Default = 25 points per amu.

		OUTPUT:
		(none)

		EXAMPLE:
		>>> MS = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2016234-if00-port0' , label = 'MS_MINIRUEDI_TEST', max_buffer_points = 1000 )
		>>> MS.filament_on()
		>>> MS.tune_peak_position([14,18,28,32,40,44,84],[0.2,0.2,0.025,0.1,0.4,0.1,2.4],['F','F','F','F','F','M','M'],10)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		# check for range of input values:
		N = len(peaks)
		mmz = [];
		for i in range(N):
			mmz.append(peaks[i][0])
		if len(list(set(mmz))) < 2:
			error ('Need at least two distinct mz values to tune peak positions!')

		ii = 1 # first iteration
		tuning_successful = False
		doTune = True
		while doTune:
			if ii == 1:
				if use_defaults:
					RI0 = self.get_default_RI()
					if not RI0:
						RI0 = self.get_RI()
					else:
						self.set_RI(RI0)

					RS0 = self.get_default_RS()
					if not RS0:
						RS0 = self.get_RS()
					else:
						self.set_RS(RS0)

			RI0 = self.get_RI()
			RS0 = self.get_RS()

			self.log('Before tuning (cycle ' + str(ii) +'): RI = ' + str(RI0) + 'V, RS = ' + str(RS0) + 'V')
			
			# prepare lists for delta-m values determined from the various peaks:
			delta_m = []

			# scan peaks and find peak centers:
			for k in range(0,N):

				# scan peak at mz[k]:
				mz   = peaks[k][0];
				w    = peaks[k][1];
				gate = peaks[k][2];
				det  = peaks[k][3];			
				self.log('Scanning peak at mz = ' + str(mz) + '...' )
				self.set_detector(det)

				MZ,Y,U = self.scan(mz-w,mz+w,resolution,gate,'nofile')
				
				# subtract baseline
				yL = (Y[0]+Y[1])/2
				yR = (Y[-1]+Y[-2])/2
				mL = (MZ[0]+MZ[1])/2
				mR = (MZ[-1]+MZ[-2])/2
				fit = numpy.polyfit([mL,mR],[yL,yR],1)
				fit_fn = numpy.poly1d(fit)
				Y = Y - fit_fn(MZ) # subtract baseline (straight trend line)
				Y = Y - min(Y) # force min(Y) to zero (to avoid bad cum-sum data)

				# analyse cumulative sum of peak (median center of peak):
				CY = numpy.cumsum(Y)
				dMZ = (MZ[1]-MZ[0])/2
				CMZ = [u + dMZ for u in MZ] # MZ values of cumulative sum, offset by dMZ relative to MZ

				self.plot_scan(MZ,Y,U , CMZ,CY )

				CYmax = max(CY)
				cy = [ x/CYmax for x in CY ]
				a = [ i for i in range(0,len(cy)) if cy[i] > 0.5 ] # indices to all occurrences of cy > 0.5
				b = [ i for i in range(0,len(cy)) if cy[i] <= 0.5 ] # indices to all occurrences of cy <= 0.5
				if len(a) > 0:
					a = a[0]
				else:
					a = 0
				if len(b) > 0:
					b = b[-1]
				else:
					b = 0
				if a > b:
					m1 = CMZ[a] + (0.5-cy[a])/(cy[b]-cy[a])*(CMZ[b]-CMZ[a]) # interpolated CMZ value at cy = 0.5
					self.log('Median peak center: mz = ' + '{:.3f}'.format(m1) )

				else:
					self.warning('Could not determine median peak centre from cumulative sum.' )
					m1 = numpy.nan

				# use values close to peak maximum to find peak center:
				m2 = [ MZ[j] for j,i in enumerate(Y) if i>=0.80*max(Y)] # mz values of YY values >= 0.75*max(YY)
				m2 = sum(m2) / len(m2)
				self.log('Center of mass of values > 80% of peak-max: mz = ' + '{:.3f}'.format(m2) )

				# mean of m1 and m2:
				if numpy.isnan(m1) or numpy.isnan(m2):
					delta_m.append(numpy.nan)
					self.warning('Could not reliably determine peak center. Ignoring this peak...' )
				else:
					if abs(m1-m2) > 0.35:
						self.warning('Peak center values determined from peak top and peak median differ by more than 0.35, ignoring peak at mz = ' + str(mz) + '. Consider using a peak at a different mz value for tuning!')
						delta_m.append(numpy.nan)
					else:
						m = (m1+3*m2)/4
						#m = m2
						self.log(( 'Peak center at mz = ' + '{:.3f}'.format(m) ) )
						delta_m.append(mz-m) # delta_m positive <==> peak shows up a low mass, should be shifted towards higher mz value

			# fit first-order polynomial function to mz vs. delta_m:
			kk = ~numpy.isnan(delta_m)
			nn = len(mmz)
			x = [ mmz[i] for i in range(0,nn) if kk[i] ]
			y = [ delta_m[i] for i in range(0,nn) if kk[i] ]
			fit = numpy.polyfit(x,y,1)
			fit_fn = numpy.poly1d(fit)

			# estimate delta-m at mz=0 and mz=128
			delta_m0   = fit_fn(0)
			delta_m128 = fit_fn(128)

			self.log('mz-offset at mz = 0: ' + str(delta_m0) )
			self.log('mz-offset at mz = 128: ' + str(delta_m128) )

			if abs(delta_m0) < max_delta_mz:
				if abs(delta_m128) < max_delta_mz:
					self.log('Peak positions are within tolerance (delta-mz = ' + str(max_delta_mz) + '). Tuning completed.' )
					doTune = False
					tuning_successful = True
			
			# determine new values of RI and RS if tuning is yet within tolerance:
			if doTune:
				delta_m0   = (0.5 + 0.5/max_iter**0.5) * delta_m0
				delta_m128 = (0.5 + 0.5/max_iter**0.5) * delta_m128
				ri = RI0 - delta_m0*(RS0/128)
				rs = RS0 * mz/(mz+delta_m128)

				self.set_RI(ri)
				self.set_RS(rs)
				
				# next iteration:
				ii = ii+1
				if ii > max_iter:
					self.log('Tuning completed after ' + str(max_iter) + ' iterations.' )
					doTune = False
					
		return tuning_successful



########################################################################################################



	def set_RI(self,x):
		'''
		rgams_SRS.set_RI(x)

		Set RI parameter value (peak-position tuning at low mz range / RF voltage output at 0 amu, in mV)

		INPUT:
		x: RI voltage (mV)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if (x < -86.0) or ( x > 86.0):
			error ('RI value out of allowed range (-86...+86V)')
		if x >= 0:
			x = '+' + '{:.4f}'.format(x)
		else:
			x = '{:.4f}'.format(x)

		self.param_IO('RI' + x,0)
		self.log('Set RI voltage to ' + x + 'V')



########################################################################################################



	def set_RS(self,x):
		'''
		rgams_SRS.set_RS(x)

		Set RS parameter value (peak-position tuning at high mz range / RF voltage output at 128 amu, in mV)

		INPUT:
		x: RS voltage (mV)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if (x < 600.0) or ( x > 1600.0):
			error ('RS value out of allowed range (600...+1600V)')

		x = '{:.4f}'.format(x)

		self.param_IO('RS' + x,0)
		self.log('Set RS voltage to ' + x + 'V' )



########################################################################################################



	def get_RI(self):
		'''
		x = rgams_SRS.get_RI(x)

		Get current RI parameter value (peak-position tuning at low mz range / RF voltage output at 0 amu, in mV).

		INPUT:
				(none)

				OUTPUT:
		x: RI voltage (in mV)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		x = float(self.param_IO('RI?',1))
		
		if ( x < -86.0 ) or ( x > 86.0 ) :
			error ('Could not determine current RI setting, or RI value returned was out of bounds (-86V...+86V)')

		return x



########################################################################################################



	def get_RS(self):
		'''
		x = rgams_SRS.get_RS(x)

		Get current RS parameter value (peak-position tuning at high mz range / RF voltage output at 128 amu, in mV)

		INPUT:
		(none)

		OUTPUT:
		x: RS voltage (in mV)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		x = float(self.param_IO('RS?',1))

		if ( x < 600.0 ) or ( x > 1600.0 ) :
			error ('Could not determine current RS setting, or RS value returned was out of bounds (600V...1600V)')

		return x



########################################################################################################



	def get_DI(self):
		'''
		x = rgams_SRS.get_DI(x)

		Get current DI parameter value (peak-width tuning at low mz range)

		INPUT:
				(none)

				OUTPUT:
		x: DI value (bit units)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		x = float(self.param_IO('DI?',1))

		if ( x < 0 ) or ( x > 255 ) :
			error ('Could not determine current DI setting, or DI value returned was out of bounds (0...255)')

		return x



########################################################################################################



	def get_DS(self):
		'''
		x = rgams_SRS.get_DS(x)

		Get current DS parameter value (peak-width tuning at high mz range)

		INPUT:
				(none)

				OUTPUT:
		x: DS value (bit/amu units)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		x = float(self.param_IO('DS?',1))

		if ( x < -2.55 ) or ( x > 2.55 ) :
			error ('Could not determine current DS setting, or DS value returned was out of bounds (-2.55...2.55)')

		return x


########################################################################################################



	def set_DI(self,x):
		'''
		rgams_SRS.set_DI(x)

		Set DI parameter value (Peak width parameter at m/z = 0)

		INPUT:
		x: parameter value (bit units)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if (x < 0.0) or ( x > 255.0):
			error ('DI value out of allowed range (0...255 bit units)')

		x = '{:.4f}'.format(x)

		self.param_IO('DI' + x,0)
		self.log('Set DI value to ' + x + ' bit units' )



########################################################################################################



	def set_DS(self,x):
		'''
		rgams_SRS.set_DS(x)

		Set DS parameter value (Peak width parameter for m/z > 0)

		INPUT:
		x: parameter value (bit/amu units)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if (x < -2.55) or ( x > 2.55):
			error ('DS value out of allowed range (-2.55...2.55 bit/amu units)')

		x = '{:.4f}'.format(x)

		self.param_IO('DS' + x,0)
		self.log('Set DS value to ' + x + ' bit/amu' )



########################################################################################################



	def plot_peakbuffer(self):
		'''
		rgams_SRS.plot_peakbuffer()

		Plot trend (or update plot) of values in PEAKs data buffer (e.g. after adding data)
		NOTE: plotting may be slow, and it may therefore be a good idea to keep the update interval low to avoid affecting the duty cycle.

		INPUT:
		(none)

		OUTPUT:
		(none)
		'''

		if not self._has_display:
			if not self._has_external_display:
				self.warning('Plotting of peakbuffer trend not possible (no display system available).')

		else:
			
			try: # make sure data analysis does not fail due to a silly plotting issue

				if not self._figwindow_is_shown:
					# show the window on screen
					self._fig.show()
					self._figwindow_is_shown = True
				
				# remove all the lines that are currently in the plot:
				self._peakbuffer_ax.lines = []

				# redo the plot by plotting line by line (mz by mz and detector by detector):
				colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k') # some colors for use with all 'other' mz values
				n = 0
				leg = []
				t0 = misc.now_UNIX()			
				N = len(self._peakbuffer_mz)

				X_MIN = None
				X_MAX = None

				if self._peakbufferplot_yscale == 'log':
					Y_MIN = 0.1
					Y_MAX = 10

				else:
					Y_MIN = 1
					Y_MAX = 1

				for mz in numpy.unique(self._peakbuffer_mz): # loop through all mz values in the peak buffer
					for det in [ 'F' , 'M' ]: # loop through all detectors (Faraday and Multiplier)
						k = [ i for i in range(N) if ((self._peakbuffer_mz[i] == mz) & (self._peakbuffer_det[i] == det)) ] # index to data with current mz / detector pair
						if len(k) > 0: # if k is not empty
							# col = colors[n%7]
							intens0 = self._peakbuffer_intens[k[0]]
							col = [c for c in self._peakbufferplot_colors if c[0] == mz]
							if col:
								col = col[0][1]
							else:
								col = colors[n%7]
							if det == 'F':
								style = 'o'
							elif det == 'M':
								style = 's'
							else:
								style = 'x'
							
							yy = self._peakbuffer_intens[k]/intens0
							tt = self._peakbuffer_t[k] - t0

							self._peakbuffer_ax.plot( tt , yy , color=col, marker=style , linestyle='-' , linewidth=1 , markersize=10) 

							val_min = self._peakbuffer_intens[k].min()
							val_max = self._peakbuffer_intens[k].max()
							min = "{:.2e}".format(val_min)
							max = "{:.2e}".format(val_max)
							leg.append( 'mz=' + str(int(mz)) + ' det=' + det + ': ' + min + ' ... ' + max + ' ' + self._peakbuffer_unit[k[0]] )
							
							if X_MIN == None:
								X_MIN = tt.min()
							if X_MAX == None:
								X_MAX = tt.min()
							if tt.min() < X_MIN:
								X_MIN = tt.min()
							if tt.max() > X_MAX:
								X_MAX = tt.max()
	
							if yy.min() < Y_MIN:
								Y_MIN = yy.min()
							if yy.max() > Y_MAX:
								Y_MAX =	yy.max()
							
							n = n+1
			
				if len(self._peakbuffer_ax.lines) > 0: # if the plot is not empty
					
					# set legend location:
					self._peakbuffer_ax.legend( leg , loc='best' , prop={'size':9} )

					# set title and axis labels:
					t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(t0))
					self._peakbuffer_ax.set_title('PEAKBUFFER (' + self.label() + ') at ' + t0)
					self._peakbuffer_ax.set_xlabel('Time (s)')
					self._peakbuffer_ax.set_ylabel('Intensity (rel.)')

					# Set x-axis scaling:
					DX = 0.05*(X_MAX-X_MIN);
					if DX == 0:
						DX = 5
					self._peakbuffer_ax.set_xlim( [ X_MIN-DX , X_MAX+DX ] )

					# Set y-axis scaling:
					if Y_MIN < self._peakbuffer_plot_min_y:
						Y_MIN = self._peakbuffer_plot_min_y
					if Y_MAX > self._peakbuffer_plot_max_y:
						Y_MAX = self._peakbuffer_plot_max_y

					if self._peakbufferplot_yscale == 'log':
						self._peakbuffer_ax.set_ylim( [ Y_MIN , Y_MAX ] )

					else:		
						if Y_MIN < Y_MAX:
							DY = 0.05*(Y_MAX-Y_MIN)
						else:
							DY = 0.001
						self._peakbuffer_ax.set_ylim( [ Y_MIN-DY , Y_MAX+DY ] )


				# Update the plot:
				self._fig.canvas.flush_events()
				

			except:
				self.warning( 'Error during plotting of peakbuffer trend (' + str(sys.exc_info()[0]) + ').' )



	########################################################################################################



	def set_peakbuffer_plot_min_y(self,val):
		'''
		rgams_SRS.set_peakbuffer_plot_min_y(val)

		Set lower limit of y range in peakbuffer plot.

		INPUT:
		val: lower limit of y-axis range

		OUTPUT:
		(none)
		'''

		self._peakbuffer_plot_min_y = val



	########################################################################################################



	def set_peakbuffer_plot_max_y(self,val):
		'''
		rgams_SRS.set_peakbuffer_plot_max_y(val)

		Set upper limit of y range in peakbuffer plot.

		INPUT:
		val: upper limit of y-axis range

		OUTPUT:
		(none)
		'''

		self._peakbuffer_plot_max_y = val



	########################################################################################################



	def set_peakbuffer_mz_color(self,mz,col):
		'''
		rgams_SRS.set_peakbuffer_mz_color(mz,col)
		
		Set color to be used for given m/z value in peakbuffer plot.
		
		INPUT:
		mz: m/z value
		col: color (string), for example col = 'r' or col = 'darkgray'; see Python/Matplotlib documentation for details.
		
		OUTPUT:
		(none)
		'''

		mz = round(mz) # just in case mz was not an integer
		found = False

		# check for existing entry for this m/z, and replace color:
		for k in range(len(self._peakbufferplot_colors)-1):
			if self._peakbufferplot_colors[k][0] == mz:
				self._peakbufferplot_colors[k] = (mz,col)
				found = True
				break
		
		if found == False:
			# append new mz/color combo if it did not yet exist:
			self._peakbufferplot_colors.append((mz,col))



	########################################################################################################



	def plot_scan(self,mz,intens,unit,cumsum_mz=[],cumsum_val=[]):
		'''
		rgams_SRS.plot_scan(mz,intens,unit,cumsum_mz=[],cumsum_val=[])

		Plot scan data

		INPUT:
		mz: mz values (x-axis)
		intens: intensity values (y-axis)
		unit: intensity unit (string)
		cumsum_mz,cumsum_val (optional): cumulative sum of peak data (mz and sum values), as used for peak centering

		OUTPUT:
		(none)
		'''

		if not self._has_display:
			self.warning('Plotting of scan data not possible (no display system available).')

		else:
		
			try: # make sure data analysis does not fail due to a silly plotting issue

				if not self._figwindow_is_shown:
					# show the window on screen
					self._fig.show()
					self._figwindow_is_shown = True

				# remove all the lines that are currently in the plot:
				self._scan_ax.lines = []

				self._scan_ax.plot( mz , intens , 'k.-' )
				if cumsum_mz:
					# normalize cumulative sum values to intens (to match plot scales):
					cumsum_val = cumsum_val / max(cumsum_val) * max(intens)
					# add cumulative sum data to plot:
					self._scan_ax.plot( cumsum_mz , cumsum_val , 'r.-' )

				self._scan_ax.set_xlabel('mz')
				self._scan_ax.set_ylabel('Intensity (' + unit +')')
				t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(misc.now_UNIX()))
				self._scan_ax.set_title('SCAN (' + self.label() + ')' + ' at ' + t0)
				self._fig.tight_layout(pad=1.5)

				# Set axis scaling (automatic):
				self._scan_ax.relim()
				self._scan_ax.autoscale_view()

				# update the plot:
				self._fig.canvas.flush_events()

			except:
				self.warning( 'Error during plotting of scan data (' + str(sys.exc_info()[0]) + ').' )

			
	########################################################################################################


	def print_status(self, stdout = True):
		'''
		rgams_SRS.print_status(stdout = True)

		Print status of the RGA head.

		INPUT:
		stdout: flag to control output to STDOUT (default: stdout = True)

		OUTPUT:
		status: string containing status information
		'''

		status  = 'SRS RGA status:\n'
		status += '   MS max m/z range: ' + str(self.mz_max()) + '\n'
		status += '   Ionizer electron energy: ' + str(self.get_electron_energy()) + ' eV\n'
		status += '   Electron emission current: ' + str(self.get_electron_emission()) + ' mA\n'
		if self.has_multiplier():
			status += '   MS has electron multiplier installed (default bias voltage = ' + str(self.get_multiplier_default_hv()) + ' V)\n'
			det = self.get_detector()
			if det == 'M':
				det = det + ' (bias voltage = ' + self.get_multiplier_hv() + ' V)'
			status += '   Currently active detector: ' + det + '\n'

		else:
			status += '   MS does not have electron multiplier installed (Faraday only).\n'
		status += '   Current mz-tuning:\n'
		status += '      RI = ' + str(self.get_RI()) + ' mV (RF output at 0 amu)\n'
		status += '      RS = ' + str(self.get_RS()) + ' mV (RF output at 128 amu)\n'
		status += '      DI = ' + str(self.get_DI()) + ' bit units (Peak width parameter at m/z = 0)\n'
		status += '      DS = ' + str(self.get_DS()) + ' bit/amu units (Peak width parameter for m/z > 0)\n'

		# check for MS/RGA errors:
		errstatus = int(self.param_IO('ER?',1))
		if errstatus == 0:
			status += 'Error status: no errors found.\n'
		else:
			# Found an error with the MS/RGA! Determine and show error information
			status += 'Error status:\n'
			if errstatus & 0b00000001:
			# RS232 communication problem
				err = int(self.param_IO('EC?',1))
				msg = 'unknown error'
				if err & 0b00000001:
					msg = 'bad command received'
				if err & 0b00000010:
					msg = 'bad parameter received'
				if err & 0b00000100:
					msg = 'command-too-long'
				if err & 0b00001000:
					msg = 'overwrite in receiving'
				if err & 0b00010000:
					msg = 'transmit buffer overwrite'
				if err & 0b00100000:
					msg = 'jumper protection violation'
				if err & 0b01000000:
					msg = 'parameter conflict'
				msg = 'RGA communications error: ' + msg + '.'
				self.warning(msg)
				status += msg + '\n'

			if errstatus & 0b00000010:
			# Filament problem
				err = int(self.param_IO('EF?',1))
				msg = 'unknown error'
				if err & 0b00000001:
					msg = 'single filament operation'
				if err & 0b00100000:
					msg = 'vacuum chamber pressure too high'
				if err & 0b01000000:
					msg = 'unable to set the requested emission current'
				if err & 0b10000000:
					msg = 'no filament detected'
				msg = 'RGA filament error: ' + msg + '.'
				self.warning(msg)
				status += msg + '\n'

			if errstatus & 0b00001000:
			# CEM problem
				err = int(self.param_IO('EM?',1))
				msg = 'unknown error'
				if err & 0b10000000:
					msg = 'no electron multiplier option installed'
				msg = 'RGA electron multiplier error: ' + msg + '.'
				self.warning(msg)
				status += msg + '\n'

			if errstatus & 0b00010000:
			# Quadrupole filter problem
				err = int(self.param_IO('EQ?',1))
				msg = 'unknown error'
				if err & 0b00010000:
					msg = 'power supply in current limited mode'
				if err & 0b01000000:
					msg = 'primary current exceeds 2.0A'
				if err & 0b10000000:
					msg = 'RF_CT exceeds (V_EXT-2V) at M_MAX'
				msg = 'RGA quadrupole mass filter error: ' + msg + '.'
				self.warning(msg)
				status += msg + '\n'

			if errstatus & 0b00100000:
			# Electrometer problem
				err = int(self.param_IO('ED?',1))
				msg = 'unknown error'
				if err & 0b00000010:
					msg = 'op-amp input offset voltage out of range'
				if err & 0b00001000:
					msg = 'compensate fails to read -5nA input current'
				if err & 0b00010000:
					msg = 'compensate fails to read +5nA input current'
				if err & 0b00100000:
					msg = 'detect fails to read -5nA input current'
				if err & 0b01000000:
					msg = 'detect fails to read +5nA input current'
				if err & 0b10000000:
					msg = 'ADC16 test failure'
				msg = 'RGA electrometer error: ' + msg + '.'
				self.warning(msg)
				status += msg + '\n'

			if errstatus & 0b01000000:
			# External PSU problem
				err = int(self.param_IO('EP?',1))
				msg = 'unknown error'
				if err & 0b01000000:
					msg = 'external 24V PS voltage <22V'
				if err & 0b10000000:
					msg = 'external 24V PS voltage >26V'
				msg = 'RGA 24V external PSU error: ' + msg + '.'
				self.warning(msg)
				status += msg + '\n'
		
		# remove newline at end:
		status = status.rstrip()
		
		if stdout:
			print(status)
			
		return status



####################################################################################################



	def peak_zero_loop (self,mz,detector,gate,ND,NC,datafile,clear_peakbuf_cond=True,clear_peakbuf_main=True,plot_cond=False,datatype=None):
		'''
		peak_zero_loop (mz,detector,gate,ND,NC,datafile,clear_peakbuf_cond=True,clear_peakbuf_main=True,plot_cond=False,datatype=None)
		
		Cycle PEAKS and ZERO readings given mz values.
		
		INPUT:
		mz: list of tuples with peak m/z value (for PEAK) and delta-mz (for ZERO). If delta-mz == 0, no ZERO value is read.
		detector: detector string ('F' or 'M')
		gate: integration time
		ND: number of data cycles recorded to the current data file
		NC: number of cycles used for conditioning of the detector and electronics before recording the data (not written to datafile)
		datafile: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		clear_peakbuf_cond: flag to set clearing of peakbuffer before conditioning cycles on/off (optional, default=True)
		clear_peakbuf_main: flag to set clearing of peakbuffer before main cycles on/off (optional, default=True)
		plot_cond: flag to set plotting of readings used for detector conditioning (inclusion of values in peakbuffer)
		datatype (optional): see 'peaktype' argument of self.peak or 'zerotype' argument of self.zero (default: datatype=None)
		OUTPUT:
		(none)
	'''


		def pz_cycle (m,g,f,typ,add_to_peakbuffer=True):
			for i in range(len(m)):
				self.peak(m[i][0],g,f,add_to_peakbuffer,peaktype=typ) # read PEAK value
				if not m[i][1] == 0:
					self.zero(m[i][0],m[i][1],g,f,zerotype=typ) # read ZERO value
			if add_to_peakbuffer:
				self.plot_peakbuffer()

		# prepare:
		self.set_detector(detector)
		
		# conditioning detector and electronics:
		if NC > 0:
			if clear_peakbuf_cond:
				self.peakbuffer_clear() # clear peakbuffer
			for i in range(NC):
				msg = 'Conditioning ' + detector + ' detector (cycle ' + str(i+1) + ' of ' + str(NC) + ')...        '
				print ( '\r' + msg , end='\r' )
				sys.stdout.flush()
				pz_cycle (mz,gate,'nofile',datatype,plot_cond)
			print ( msg.rstrip() + 'done.' )

		# reading data values:
		if ND > 0:
			if clear_peakbuf_main:
				self.peakbuffer_clear() # clear peakbuffer
			for i in range(ND):
				msg = 'Reading data using ' + detector + ' detector (cycle ' + str(i+1) + ' of ' + str(ND) + ')...        '
				print ( '\r' + msg , end='\r' )
				sys.stdout.flush()
				pz_cycle (mz,gate,datafile,datatype)
			print ( msg.rstrip() + 'done.' )



####################################################################################################


	def write_deconv_info (self,target_mz,target_species,deconv_detector,basis,f):

		'''
		write_deconv_info (target_mz,target_species,deconv_detector,basis,f)

		Write DECONVOLUTION information line to data file (information needed by the deconvolution processor).

		INPUT:
		target_mz: m/z ratio of the peak that needs "overlap correction by deconvolution" (integer)
		target_species: name of the gas species that needs "overlap correction by deconvolution" (string)
		deconv_detector: indicates whether deconvolution (regression of linear model) is based on Faraday or Multiplier data (string, eiter 'F' or 'M')
		basis: spectra (or "endmembers") to be used as basis for deconvolution (Pyhton tuple). Every tuple element is of the form ('speciesname',mz1,peakheight1,mz2,peakheight2,...,mzN,peakheightN). Example: basis=( ('CH4',13,0.12,14,0.205,15,0.902,16,1.0) , ('N2',14,0.13,15,0.00043,28,1.0,29,0.0035) , ('O2',16,0.21,32,1.0) )
		f: data file object

		OUTPUT:
		(none)
		'''
		f.write_ms_deconv('RGA_SRS',self.label(),target_mz,target_species,deconv_detector,self.get_electron_energy(),basis,misc.now_UNIX())
