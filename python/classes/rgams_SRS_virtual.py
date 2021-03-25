# Code for virtual SRS RGA mass spec class (mostly useful for development or demo purposes without acces to a real VICI valve)
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
# Copyright 2020, Matthias Brennwald (brennmat@gmail.com)

try:
	import sys
	import warnings
	import time
	import math
	import numpy
	import random
	from classes.misc	import misc
	from classes.rgams_SRS	import rgams_SRS, havedisplay
except ImportError as e:
	print (e)
	raise

if havedisplay:
	import matplotlib
	import matplotlib.pyplot as plt

class rgams_SRS_virtual(rgams_SRS):
	"""
	ruediPy class for virtual SRS RGA-MS
	"""


	########################################################################################################


	def __init__( self , serialport=None , label='MS' , cem_hv = 1400 , tune_default_RI = [] , tune_default_RS = [] , max_buffer_points = 500 , fig_w = 10 , fig_h = 8 , peakbuffer_plot_min=0.5 , peakbuffer_plot_max = 2 , peakbuffer_plot_yscale = 'linear' , scan_plot_yscale = 'linear' , has_plot_window = True , has_external_plot_window = None):

		'''
		rgams_SRS_virtual.__init__( serialport , label='MS' , cem_hv = 1400 , tune_default_RI = [] , tune_default_RS = [] , max_buffer_points = 500 , fig_w = 10 , fig_h = 8 , peakbuffer_plot_min=0.5 , peakbuffer_plot_max = 2 , peakbuffer_plot_yscale = 'linear' , scan_plot_yscale = 'linear' , has_plot_window = True , has_external_plot_window = None)
		
		Initialize virtual mass spectrometer (SRS RGA)
		
		INPUT:
		serialport (optional): device name of the serial port, e.g. P = '/fake/serialport/to/virtual/rga_MS'
		label (optional): label / name of the RGAMS object (string). Default: label = 'MS'
		cem_hv (optional): default bias voltage to be used with the electron multiplier (CEM). Default value: cem_hv = 1400 V.
		tune_default_RI (optional): default RI parameter value in m/z tuning. Default value: tune_RI = []
		tune_default_RS (optional): default RS parameter value in m/z tuning. Default value: tune_RS = []
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500
		fig_w, fig_h (optional): width and height of figure window used to plot data (inches). 
		peakbuffer_plot_min, peakbuffer_plot_max (optional): limits of y-axis range in peakbuffer plot (default: peakbuffer_plot_min=0.5 , peakbuffer_plot_max = 2)
		peakbuffer_plot_yscale (optional) = y-axis scaling for peakbuffer plot (default: 'linear', use 'log' for log scaling)
		scan_plot_yscale (optional) = y-axis scaling for scan plot (default: 'linear', use 'log' for log scaling)

		has_plot_window (optional): flag to choose if a plot window should be opened for the rgams_SRS object (default: has_plot_window = True)
		has_external_plot_window (optional) = flag to indicate if external plot window is used instead of the "built-in" window. If set to True, this will override the 'has_plot_window' flag (default: has_external_plot_window = False).

		OUTPUT:
		(none)
		'''

		# object name label (do this first, so the label/name is set for warning or log messages or exception handling):
		self._label = label
			
		# Check for has_external_plot_window flag:
		if has_external_plot_window is None:
			has_external_plot_window = misc.have_external_gui()

		# general parameters:
		self._serialport = serialport;
		self._serial_number = 123456789
		self._cem_hv = float(cem_hv)
		self._tune_default_RI = tune_default_RI
		self._tune_default_RS = tune_default_RS
		
		if not tune_default_RI == []:
			self._RI = tune_default_RI
		else:
			self._RI = -9.0
		if not tune_default_RS == []:
			self._RS = tune_default_RS
		else:
			self._RS = 1070.0

		self._DI = 116
		self._DS = -0.01

		self._EE = 70
		self._FL = 0.0
		self._hasmulti = True
		self._mzmax = 200
		self._noisefloor = 3
		
		# init MS settings:
		self.set_detector('F')
		self.filament_off()
		
		# peakbuffer:
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

		# y-axis scaling for scan plot:
		self._scan_yscale = scan_plot_yscale

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

		self.log( 'Successfully configured virtual SRS RGA MS with serial number ' + str(self._serial_number) + ' on ' + serialport )
		

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
				det = det + ' (bias voltage = ' + str(self.get_multiplier_hv()) + ' V)'
			status += '   Currently active detector: ' + det + '\n'

		else:
			status += '   MS does not have electron multiplier installed (Faraday only).\n'
		status += '   Current mz-tuning:\n'
		status += '      RI = ' + str(self.get_RI()) + ' mV (RF output at m/z = 0)\n'
		status += '      RS = ' + str(self.get_RS()) + ' mV (RF output at m/z = 128)\n'
		status += '      DI = ' + str(self.get_DI()) + ' bit units (Peak width parameter at m/z = 0\n'
		status += '      DS = ' + str(self.get_DS()) + ' bit/amu units (Peak width parameter for m/z > 0'
		
		# fake some time that would be needed to talk the the MS:
		time.sleep(3)
		
		if stdout:
			print(status)
		
		return status
		

	########################################################################################################
	
	
	def set_electron_energy(self,val):
		'''
		rgams_SRS_virtual.set_electron_energy(val)
		
		Set electron energy of the ionizer.
		
		INPUT:
		val: electron energy in eV
		
		OUTPUT:
		(none)
		'''
		
		self._EE = val
		time.sleep(1.5)
	

	########################################################################################################
	

	def get_electron_energy(self):
		'''
		val = rgams_SRS_virtual.get_electron_energy()
		
		Return electron energy of the ionizer (in eV).
		
		INPUT:
		(none)
		
		OUTPUT:
		val: electron energy in eV
		'''

		return self._EE


	########################################################################################################
	

	def set_multiplier_hv(self,val):
		'''
		rgams_SRS_virtual.set_multiplier_hv(val)
		
		Set electron multiplier (CEM) high voltage (bias voltage).
		
		INPUT:
		val: voltage
		
		OUTPUT:
		(none)
		'''
		
		# check if CEM option is installed:
		if self.has_multiplier():
			self._cem_hv = float(val)

		else:
			self.warning ('Cannot set multiplier (CEM) high voltage, because CEM option is not installed.')


	########################################################################################################
	

	def set_multiplier_default_hv(self, cem_hv):
		'''
		rgams_SRS_virtual.set_multiplier_default_hv(cem_hv)
		
		Set default value to be used for electron multiplier (CEM) high voltage (bias voltage). THIS FUNCTION DOES NOTHING!
		
		INPUT:
		cem_hv: see __init__
		
		OUTPUT:
		(None)
		'''

		# do nothing, as self._cem_hv is used differently with the virtual RGA than with the real RGA.
		pass

	
	########################################################################################################


	def get_multiplier_hv(self):
		'''
		val = rgams_SRS_virtual.get_multiplier_hv()
		
		Return electron multiplier (CEM) high voltage (bias voltage).
		
		INPUT:
		(none)
		
		OUTPUT:
		val: voltage
		'''
		
		# check if CEM option is installed:
		if self.has_multiplier():
			ans = self._cem_hv
		else:
			self.warning ('Cannot get multiplier (CEM) high voltage, because CEM option is not installed.')
			ans = None

		return ans
		
		
	########################################################################################################
	

	def get_multiplier_default_hv(self):
		'''
		val = rgams_SRS_virtual.get_multiplier_default_hv()
		
		Return default value to be used for electron multiplier (CEM) high voltage (bias voltage).
		NOTE: the value returned is NOT the value stored in the memory of the RGA head. This function is just a wrapper that returns the default high voltage value set in the RGA object (e.g., during initialisation of the object).
		
		INPUT:
		(none)
		
		OUTPUT:
		val: voltage
		'''

		# return some fixed number (not self._cem_hv, which is used differently for the virtual_RGA):
		return 1500.0

	
	########################################################################################################
	

	def set_electron_emission(self,val):
		'''
		rgams_SRS_virtual.set_electron_emission(val)
		
		Set electron emission current.
		
		INPUT:
		val: electron emission current in mA (0 ... 3.5 mA)
		
		OUTPUT:
		(none)
		'''
		
		self._FL = val

	
	########################################################################################################
	

	def get_electron_emission(self):
		'''
		val = rgams_SRS_virtual.get_electron_emission()
		
		Return electron emission current (in mA)
		
		INPUT:
		(none)
		
		OUTPUT:
		val: electron emission current in mA (float)
		'''
		
		return self._FL

	
	########################################################################################################
	

	def filament_on(self):
		'''
		rgams_SRS_virtual.filament_on()
		
		Turn on filament current at default current value.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''
		
		self._FL = 1.23456789
		time.sleep(1.5)

	
	########################################################################################################
	

	def filament_off(self):
		'''
		rgams_SRS_virtual.filament_off()
		
		Turn off filament current.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''
		
		self._FL = 0.0
		time.sleep(0.7)

	
	########################################################################################################
	

	def has_multiplier(self):
		'''
		val = rgams_SRS_virtual.has_multiplier()
		
		Check if MS has electron multiplier installed.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: result flag, val = 0 --> MS has no multiplier, val <> 0: MS has multiplier
		'''

		return self._hasmulti

	
	########################################################################################################
	

	def mz_max(self):
		'''
		val = rgams_SRS_virtual.mz_max()
		
		Determine highest mz value supported by the MS.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: max. supported mz value (int)
		'''

		return self._mzmax

	
	########################################################################################################
	

	def set_detector(self,det):
		'''
		rgams_SRS_virtual.set_detector(det)
		
		Set current detetector used by the MS (direct the ion beam to the Faraday or electron multiplier detector).
				
		INPUT:
		det: detecor (string):
			det='F' for Faraday
			det='M' for electron multiplier
		
		OUTPUT:
		(none)
		'''
		
		if det == 'F':
			self.set_multiplier_hv(0.0)

		elif det == 'M':
			if self.has_multiplier():
				self.set_multiplier_hv(self.get_multiplier_default_hv())
			else:
				self.warning ('RGA has no electron multiplier installed!')
		else:
			self.warning ('Unknown detector ' + det)
			

	
	########################################################################################################
	

	def get_detector(self):
		'''
		det = rgams_SRS_virtual.get_detector()
		
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
			if float(self.get_multiplier_hv()) == 0.0:
				det = 'F'
			else:
				det = 'M'

		return det

	
	########################################################################################################
	

	def get_noise_floor(self):
		'''
		val = rgams_SRS_virtual.get_noise_floor()
		
		Get noise floor (NF) parameter for RGA measurements (noise floor controls gate time, i.e., noise vs. measurement speed).
				
		INPUT:
		(none)
		
		OUTPUT:
		val: NF noise floor parameter value, 0...7 (integer)
		'''

		return self._noisefloor

	
	########################################################################################################
	


	def set_noise_floor(self,NF):
		'''
		val = rgams_SRS_virtual.set_noise_floor()
		
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
			self._noisefloor = NF



########################################################################################################



	def peak(self,mz,gate,f,add_to_peakbuffer=True,peaktype=None):
		'''
		val,unit = rgams_SRS_virtual.peak(mz,gate,f,add_to_peakbuffer=True,peaktype=None)
		
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

		if mz < 1:
			self.warning ('mz value must be positive! Skipping peak measurement...')
			val = '-1'
			unit = '(none)'
			
		elif mz > self.mz_max():
			self.warning ('mz value must be ' + str(self.mz_max()) + ' or less! Skipping peak measurement...')
			val = '-1'
			unit = '(none)'
			
		else: # proceed with measurement

			# deal with gate times longer than 2.4 seconds (max. allowed with SRS-RGA):
			v = 0.0;

			if gate > 2.4:
				N = int(round(gate/2.4))
				gt = 2.4
			else:
				N = 1
				gt = gate
			
			for k in range(N):
				
		
				# peak reading:
				time.sleep(gt)
				if self.get_electron_emission() > 0.0:
					if mz == 4:
						u = 1E-14
					elif mz == 14:
						u = 1.1E-10
					elif mz == 15:
						u = 1E-13
					elif mz == 16:
						u = 5E-13
					elif mz == 18:
						u = 1.0E-11
					elif mz == 20:
						u = 1.0E-12
					elif mz == 22:
						u = 1.0E-13
					elif mz == 28:
						u = 1.23E-9
					elif mz == 32:
						u = 2.4E-10
					elif mz == 36:
						u = 1E-13
					elif mz == 40:
						u = 3E-11
					elif mz == 44:
						u = 1E-12
					elif mz == 84:
						u = 1E-14
					else:
						u = 1E-15
				else:
					u = 1.23e-15

				u = u / 1E-16
				u = (1+(random.random()-0.5)/5) * u
				
				v = v + u
			
			v = v/N
			val = v * 1E-16 # multiply by 1E-16 to convert to Amperes
			unit = 'A'

		det = self.get_detector()
		if det == 'M':
			val = 1E4 * val
			if val > 1.3E-7:
				val = 1.3E-7
		
		if not ( f == 'nofile' ):
			f.write_peak('RGA_SRS',self.label(),mz,val,unit,det,gate,t,peaktype)
		
		# add data to peakbuffer
		if add_to_peakbuffer:
			self.peakbuffer_add(t,mz,val,det,unit)

		return val,unit
		
		
	########################################################################################################
	

	def zero(self,mz,mz_offset,gate,f,zerotype=None):
		'''
		val,unit = rgams_SRS_virtual.zero(mz,mz_offset,gate,f,zerotype=None)
		
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

			val = 1E-15
			unit = 'A'

		det = self.get_detector()
		if det == 'M':
			val = 1E4 * val
		
		if not ( f == 'nofile' ):
			f.write_zero('RGA_SRS',self.label(),mz,mz_offset,val,unit,self.get_detector(),gate,t,zerotype)

		return val,unit


	########################################################################################################


	def scan(self,low,high,step,gate,f):
		'''
		M,Y,unit = rgams_SRS_virtual.scan(low,high,step,gate,f)

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
		if low > high:
			self.warning ('Scan m/z value at start must be lower than at end. Swapping values...')
			x = low;
			low = high;
			high = x;

		# configure RGA (gate time):
		self.set_gate_time(gate)

		# get time stamp:
		t = misc.now_UNIX()

		# number of scan points:
		N = (high-low)*step
		
		# determine scan data:
		low = float(low)
		high = float(high)
		M = [low + x*(high-low)/N for x in range(N)]
		Y = []
		for mz in M:
			y  = self.peak(round(mz),gate/N,'nofile',add_to_peakbuffer=False)[0]
			y0 = self.peak(100,gate/N,'nofile',add_to_peakbuffer=False)[0]
			d = abs(mz-round(mz))
			if d > 0.35:
				# baseline:
				y = y0
			elif d > 0.15:
				# flank:
				y = y0 + 0.8*(0.35-d)/0.15*y
		
			Y.append( y )
			
		# set unit:	
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
		val = rgams_SRS_virtual.ionizer_degas(duration)
		
		Run the ionizer degas procedure (see SRS RGA manual). Only run this with sufficiently good vacuum!
						
		INPUT:
		duration: degas time in minutes (0...20 / integer)
		
		OUTPUT:
		(none)
		'''
		
		self.warning('ionizer_degas not implemented for virtual SRS RGA MS')



	########################################################################################################


	
	def calibrate_electrometer(self):
		'''
		val = rgams_SRS_virtual.calibrate_electrometer()
		
		Calibrate the electrometer I-V response curve (lookup table). See also the "CL" command in the SRS RGA manual.
				
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		self.warning('calibrate_electrometer not implemented for virtual SRS RGA MS')



	########################################################################################################

	

	def calibrate_all(self):
		'''
		val = rgams_SRS_virtual.calibrate_all()
		
		Calibrate the internal coefficients for compensation of baseline offset and peak positions. This will zero the baseline for all noise-floor (NF) and detector combinations. See also the "CA" command in the SRS RGA manual.
				
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		self.warning('calibrate_all not implemented for virtual SRS RGA MS')


########################################################################################################


	def tune_peak_position_NADABADABUM(self,peaks,max_iter=10,max_delta_mz=0.05,use_defaults=False,resolution=25):
		'''
		rgams_SRS_virtual.tune_peak_position(mz,gate,det,max_iter=10,max_delta_mz=0.05,use_defaults=False,resolution=25)

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

		self.warning('tune_peak_position not implemented for virtual SRS RGA MS')



########################################################################################################



	def set_RI(self,x):
		'''
		rgams_SRS_virtual.set_RI(x)

		Set RI parameter value (peak-position tuning at low mz range / RF voltage output at 0 amu, in mV)

		INPUT:
		x: RI voltage (mV)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if x > 86:
			self.warning ('RI parameter must not be higher than 86. Using RI = 86...')
			x = 86
		elif x < -86:
			self.warning ('RI parameter must not be lower than -86. Using RI = -86...')
			x = -86
		self._RI = x



########################################################################################################



	def set_RS(self,x):
		'''
		rgams_SRS_virtual.set_RS(x)

		Set RS parameter value (peak-position tuning at high mz range / RF voltage output at 128 amu, in mV)

		INPUT:
		x: RS voltage (mV)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if x > 1600:
			self.warning ('RS parameter must not be higher than 1600 V. Using RS = 1600 V...')
			x = 1600
		elif x < 600:
			self.warning ('RS parameter must not be lower than 600 V. Using RS = 600 V...')
			x = 600
		self._RS = x



########################################################################################################



	def get_RI(self):
		'''
		x = rgams_SRS_virtual.get_RI(x)

		Get current RI parameter value (peak-position tuning at low mz range / RF voltage output at 0 amu, in mV).

		INPUT:
				(none)

				OUTPUT:
		x: RI voltage (in mV)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		return self._RI



########################################################################################################



	def get_RS(self):
		'''
		x = rgams_SRS_virtual.get_RS(x)

		Get current RS parameter value (peak-position tuning at high mz range / RF voltage output at 128 amu, in mV)

		INPUT:
		(none)

		OUTPUT:
		x: RS voltage (in mV)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''
		
		return self._RS



########################################################################################################



	def get_DI(self):
		'''
		x = rgams_SRS_virtual.get_DI(x)

		Get current DI parameter value (peak-width tuning at low mz range)

		INPUT:
		(none)

		OUTPUT:
		x: DI value (bit units)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		return self._DI



########################################################################################################



	def get_DS(self):
		'''
		x = rgams_SRS_virtual.get_DS(x)

		Get current DS parameter value (peak-width tuning at high mz range)

		INPUT:
				(none)

				OUTPUT:
		x: DS value (bit/amu units)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		return self._DS


########################################################################################################



	def set_DI(self,x):
		'''
		rgams_SRS_virtual.set_DI(x)

		Set DI parameter value (Peak width parameter at m/z = 0)

		INPUT:
		x: parameter value (bit units)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		if x > 255:
			self.warning ('DI parameter must not be higher than 255 V. Using DI = 255...')
			x = 255
		elif x < 0:
			self.warning ('DI parameter must not be lower than 0. Using DI = 0...')
			x = 0

		self._DI = x
		self.log('Set DI value to ' + str(x) + ' bit units' )



########################################################################################################



	def set_DS(self,x):
		'''
		rgams_SRS_virtual.set_DS(x)

		Set DS parameter value (Peak width parameter for m/z > 0)

		INPUT:
		x: parameter value (bit/amu units)

		OUTPUT:
		(none)

		NOTE:
		See also the SRS RGA manual, chapter 7, section "Peak Tuning Procedure"
		'''

		self._DS = x
		self.log('Set DS value to ' + str(x) + ' bit/amu' )



########################################################################################################
