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
# Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga


import serial
import time
import struct
import numpy
import os
from classes.misc	import misc
# from classes.plots	import plots
havedisplay = "DISPLAY" in os.environ
if havedisplay: # prepare plotting environment
	import matplotlib
	matplotlib.use('GTKAgg') # use this for faster plotting
	import matplotlib.pyplot as plt


class rgams_SRS:
	"""
	ruediPy class for SRS RGA-MS control.
	"""

	
	########################################################################################################
	

	def __init__( self , serialport , label='MS' , max_buffer_points = 500 ):
		'''
		rgams_SRS.__init__( serialport , label='MS' , max_buffer_points = 500 )
		
		Initialize mass spectrometer (SRS RGA), configure serial port connection.
		
		INPUT:
		serialport: device name of the serial port, e.g. P = '/dev/ttyUSB4' or P = '/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2350938-if00-port0'
		label (optional): label / name of the RGAMS object (string). Default: label = 'MS'
		max_buffer_points (optional): max. number of data points in the PEAKS buffer. Once this limit is reached, old data points will be removed from the buffer. Default value: max_buffer_points = 500

		OUTPUT:
		(none)
		'''
		
		# open and configure serial port for communication with SRS RGA (28'800 baud, 8 data bits, no parity, 2 stop bits
		ser = serial.Serial(
			port     = serialport,
			baudrate = 28800,
			parity   = serial.PARITY_NONE,
			stopbits = serial.STOPBITS_TWO,
			bytesize = serial.EIGHTBITS,
			timeout  = 10.0
		)
		ser.flushInput() 	# make sure input is empty
		ser.flushOutput() 	# make sure output is empty
		
		self.ser = ser
		
		# object name label:
		self._label = label
		
		# data buffer for PEAK values:
		self._peakbuffer_t = numpy.array([])
		self._peakbuffer_mz = numpy.array([])
		self._peakbuffer_intens = numpy.array([])
		self._peakbuffer_det = ['x'] * 0 # empty list
		self._peakbuffer_max_len = max_buffer_points
		
		# set up plotting environment
		self._has_display = havedisplay
		if self._has_display: # prepare plotting environment and figure
			self._peakbuffer_figure = plt.figure()
			plt.ion()
			plt.draw()
			plt.show()
			self._scan_figure = plt.figure()
			plt.ion()
			plt.draw()
			plt.show()
		
		print ('Successfully configured SRS RGA-MS on ' + serialport )
		
	
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
		
		misc.warnmessage (self.label(),msg)

	
	########################################################################################################
	

	def param_IO(self,cmd,ansreq):
		'''
		ans = rgams_SRS.param_IO(cmd,ansreq)
		
		Set / read parameter value of the SRS RGA.

		INPUT:
		cmd: command string that is sent to RGA (see RGA manual for commands and syntax)
		ansreq: flag indicating if answer from RGA is expected:
			ansreq = 1: answer expected, check for answer
			ansreq = 0: no answer expected, don't check for answer
		
		OUTPUT:
		ans: answer / result returned from RGA
		'''
	
		# check if serial buffer (input) is empty (just in case, will be useful to catch errors):
		if self.ser.inWaiting() > 0:
			self.warning('**** DEBUGGING INFO: serial buffer not empty before executing command = ' + cmd + '.')

		# send command to serial port:
		self.ser.write(cmd + '\r\n')
		
		if ansreq:

			# wait for response
			t = 0
			dt = 0.1
			doWait = 1
			while doWait:
				if self.ser.inWaiting() == 0: # wait
					time.sleep(dt)
					t = t + dt
					if t > 10: # give up waiting
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
					ans = ans + self.ser.read() # read each byte
				ans = ans.rstrip('\r\n') # remove newline characters at end
		
			# return the result:
			return ans
			
		else: # check if serial buffer is empty (will be useful to catch errors):
			if self.ser.inWaiting() > 0:
				self.warning('**** DEBUGGING INFO: serial buffer not empty after executing command = ' + cmd + ' ans = ' + ans)
			
	
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
		
		# send command to serial port:
		self.param_IO('EE' + str(val),1)

	
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
		ans = self.param_IO('EE?',1)
		return ans

	
	########################################################################################################
	

	def set_filament_current(self,val):
		'''
		rgams_SRS.set_filament_current(val)
		
		Set filament current.
		
		INPUT:
		val: current in mA
		
		OUTPUT:
		(none)
		'''
			
		# send command to serial port:
		self.param_IO('FL' + str(val),1)

	
	########################################################################################################
	

	def get_filament_current(self):
		'''
		val = rgams_SRS.get_filament_current()
		
		Return filament current (in mA)
		
		INPUT:
		(none)
		
		OUTPUT:
		val: filament current in mA
		'''
				
		# send command to serial port:
		ans = self.param_IO('FL?',1)
		return ans

	
	########################################################################################################
	

	def filament_on(self):
		'''
		rgams_SRS.filamenOn()
		
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
		self.set_filament_current(0)

	
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
			self._hasmulti = self.param_IO('MO?',1) # remember for next time
		return self._hasmulti

	
	########################################################################################################
	

	def mz_max(self):
		'''
		val = rgams_SRS.mz_max()
		
		Determine highest mz value supported by the MS.
		
		INPUT:
		(none)
		
		OUTPUT:
		val: max. supported mz value 
		'''

		if hasattr(self, '_mzmax') == 0: # never asked for mz_max before
			x = self.param_IO('MF?',1) # get current MF value
			self.param_IO('MF*',0) # set MF to default value, which equals M_MAX
			self._mzmax = self.param_IO('MF?',1) # read back M_MAX value
			self.param_IO('MF' + x,0) # set back to previous MF value
		return self._mzmax

	
	########################################################################################################
	

	def set_detector(self,det):
		'''
		rgams_SRS.set_detector()
		
		Set current detetector used by the MS (direct the ion beam to the Faraday or electron multiplier detector).
		
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
				self.param_IO('HV*',1)
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
			hv = float(hv)
			if hv == 0:
				det = 'F'
			else:
				det = 'M'
		
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
			self._noisefloor = self.param_IO('NF?',1) # get current NF value
			
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
		
		Set noi floor (NF) parameter for RGA measurements according to desired gate time (by choosing the best-match NF value).
				
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
		
		gt = numpy.array([ 2.4 , 1.21 , 0.48 , 0.25 , 0.163 , 0.060 , 0.043 , 0.025 ])
		NF  = (numpy.abs(gt-gate)).argmin() # index to closest gate time
		if gate > gt.max():
			self.warning('gate time cannot be more than ' + str(gt.max()) +'s! Using gate = ' + str(gt.max()) +'s...')
		elif gate < gt.min():
			self.warning('gate time cannot be less than ' + str(gt.min()) +'s! Using gate = ' + str(gt.min()) +'s...')
			
		self.set_noise_floor(NF)

	
	########################################################################################################
	

	def peakbuffer_add(self,t,mz,intens,det):
		"""
		rgams_SRS.peakbuffer_add(t,mz,intens)
		
		Add data to PEAKS data buffer
				
		INPUT:
		t: epoch time
		mz: mz values (x-axis)
		intens: intensity values (y-axis)
		det: detector (char/string)
		
		OUTPUT:
		(none)
		"""
				
		self._peakbuffer_t = numpy.append( self._peakbuffer_t , t )
		self._peakbuffer_mz = numpy.append( self._peakbuffer_mz , mz )
		self._peakbuffer_intens = numpy.append( self._peakbuffer_intens , intens )
		self._peakbuffer_det.append( det )
		
		N = self._peakbuffer_max_len
		
		if self._peakbuffer_t.shape[0] > N:
			self._peakbuffer_t 		= self._peakbuffer_t[-N:]
			self._peakbuffer_mz 		= self._peakbuffer_mz[-N:]
			self._peakbuffer_intens	    = self._peakbuffer_intens[-N:]
			self._peakbuffer_det	    = self._peakbuffer_det[-N:]


	########################################################################################################


	def peak(self,mz,gate,f):
		'''
		val,unit = rgams_SRS.peak(mz,gate,f)
		
		Read out detector signal at single mass (m/z value).
		
		INPUT:
		mz: m/z value (integer)
		gate: gate time (seconds)
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		
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
		
		if mz < 1:
			self.warning ('mz value must be positive! Skipping peak measurement...')
			val = '-1'
			unit = '(none)'
			
		elif mz > self.mz_max:
			self.warning ('mz value must be ' + self.mz_max + ' or less! Skipping peak measurement...')
			val = '-1'
			unit = '(none)'
			
		else: # proceed with measurement
						
			# configure RGA (gate time):
			self.set_gate_time(gate)
			
			# send command to RGA:
			self.ser.write('MR' + str(mz) + '\r\n')
			
			# get timestamp
			t = misc.now_UNIX()
			
			# read back data:
			u = self.ser.read()
			u = u + self.ser.read()
			u = u + self.ser.read()
			u = u + self.ser.read()
			
			# parse result:
			u = struct.unpack('<i',u)[0] # unpack 4-byte data value
			val = u * 1E-16 # multiply by 1E-16 to convert to Amperes
			unit = 'A'
		
		det = self.get_detector()
		
		if not ( f == 'nofile' ):
			f.write_peak('RGA_SRS',self.label(),mz,val,unit,det,gate,t)
		
		# add data to peakbuffer
		self.peakbuffer_add(t,mz,val,det)

		return val,unit
		
		
	########################################################################################################
	

	def zero(self,mz,mz_offset,gate,f):
		'''
		val,unit = rgams_SRS.zero(mz,mz_offset,gate,f)
		
		Read out detector signal at single mass with relative offset to given m/z value (this is useful to determine the baseline near a peak at a given m/z value), see rgams_SRS.peak())
		The detector signal is read at mz+mz_offset
		
		INPUT:
		mz: m/z value (integer)
		mz_offset: offset relative m/z value (integer).
		gate: gate time (seconds)
		f: file object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.
		
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
		
		if mz+mz_offset < 1:
			self.warning ('mz+mz_offset must be positive! Skipping zero measurement...')
			val = '-1'
			unit = '(none)'
			
		elif mz+mz_offset > self.mz_max:
			self.warning ('mz+mz_offset value must be ' + self.mz_max + ' or less! Skipping zero measurement...')
			val = '-1'
			unit = '(none)'
			
		else: # proceed with measurement
						
			# configure RGA (gate time):
			self.set_gate_time(gate)
			
			# send command to RGA:
			self.ser.write('MR' + str(mz+mz_offset) + '\r\n')
			
			# get timestamp
			t = misc.now_UNIX()
			
			# read back data:
			u = self.ser.read()
			u = u + self.ser.read()
			u = u + self.ser.read()
			u = u + self.ser.read()
			
			# parse result:
			u = struct.unpack('<i',u)[0] # unpack 4-byte data value
			val = u * 1E-16 # multiply by 1E-16 to convert to Amperes
			unit = 'A'
						
		if not ( f == 'nofile' ):
			f.write_zero('RGA_SRS',self.label(),mz,mz_offset,val,unit,self.get_detector(),gate,t)

		return val,unit

	
	########################################################################################################
	
	
	def scan(self,low,high,step,gate,f):
		'''
		M,Y,unit = rgams_SRS.scan(low,high,step,gate,f,p)
		
		Analog scan
		
		INPUT:
		low: low m/z value
		high: high m/z value
		step: scan resolution (number of mass increment steps per amu)
		   step = integer number --> use given number (high number equals small mass increments between steps)
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
		low = int(low)
		high = int(high)
		step = int(step)
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
			self.warning ('Scan must end at m/z=' + self.mz_max() + ' or lower! Ending at m/z= ' + self.mz_max + '...')
			low = self.mz_max()
		if low >= high:
			self.warning ('Scan m/z value at start must be lower than at end. Swapping values...')
			x = low;
			low = high;
			high = x;
		
		# configure RGA (gate time):
		self.set_gate_time(gate)

		# configure scan:
		self.param_IO('MI' + str(low),0) # low end mz value
		self.param_IO('MF' + str(high),0) # high end mz value
		self.param_IO('SA' + str(step),0) # number of steps per amu
		N = self.param_IO('AP?',1) # number of data points in the scan
		N = int(N)
		
		# start the scan:
		self.ser.write('SC1\r\n')

		# get time stamp before scan
		t1 = misc.now_UNIX()
		
		# read back result from RGA:
		Y = [] # init empty list
		k = 0
		nb = 0 # number of bytes read
		u = ''
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
				u = u + self.ser.read() # read next byte
				nb = nb + 1 # increase byte-number counter
				if nb == 4: # all four bytes for next value read, parse data
					if k < N: # if this was not the final data point (total pressure)
						u = struct.unpack('<i',u)[0] # unpack 4-byte data value
						u = u * 1E-16 # divide by 1E-16 to convert to Amperes
						Y.append(u) # append value to list 'ans'
			
					# prepare for next value:
					k = k + 1
					u = ''
					nb = 0
		
		# get time stamp after scan
		t2 = misc.now_UNIX()
		
		# flush the remaining data from the serial port buffer (total pressure measurement):
		#time.sleep(0.5) # wait a little to get all the data into the buffer
		#self.ser.flushInput() 	# make sure input is empty
		#self.ser.flushOutput() 	# make sure output is empty

		# determine scan mz values:	
		low = float(low)
		high = float(high)
		M = [low + x*(high-low)/N for x in range(N)]
		unit = 'A'
		
		# determine "mean" timestamp
		t = (t1 + t2) / 2.0

		# write to data file:
		if not ( f == 'nofile' ):
			det = self.get_detector()
			# print det
			f.write_scan('RGA_SRS',self.label(),M,Y,unit,det,gate,t)
				
		return M,Y,unit

	
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
			self.warning('Plotting of peakbuffer trend not possible (no display system available).')
		
		else:
			MZ = numpy.unique(self._peakbuffer_mz) # unique list of all mz values
			
			colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
			
			plt.figure(self._peakbuffer_figure.number)
			n = 0
			t0 = misc.now_UNIX()
			
			plt.show(block=False)
			leg = [''] * MZ.shape[0] # initialize empy legend entries			
			t0 = misc.now_UNIX()
			for mz in MZ:
				k = numpy.where( self._peakbuffer_mz == mz )[0]
				col = colors[n%7]
				# intens0 = self._peakbuffer_intens[k[0]]
				# plt.plot( self._peakbuffer_t[k] - t0 , self._peakbuffer_intens[k]/intens0 , col + 'o-' )
				plt.plot( self._peakbuffer_t[k] - t0 , self._peakbuffer_intens[k] , col + '.-' )
				plt.hold(True)
				leg[n] = 'mz='+str(int(mz))
				n = n+1
					
			plt.hold( False )
			plt.legend( leg , loc=3 )
			
			t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(t0))
			
			plt.title('PEAK VALUES (' + self.label() + ') at ' + t0)
			plt.xlabel('Time (s)')
			plt.ylabel('Intensity')
			plt.yscale('log')
			plt.draw()

	
	########################################################################################################
	
	
	def plot_scan(self,mz,intens,unit):
		'''
		rgams_SRS.plot_scan(mz,intens,unit)
		
		Plot scan data
		
		INPUT:
		mz: mz values (x-axis)
		intens: intensity values (y-axis)
		unit: intensity unit (string)
		
		OUTPUT:
		(none)
		'''
		
		if not self._has_display:
			self.warning('Plotting of scan data not possible (no display system available).')
		
		else:
			plt.figure(self._scan_figure.number)
			plt.plot( mz , intens , 'b.-' )
			plt.xlabel('m/z')
			plt.ylabel('Intensity (' + unit +')')
			t0 = time.strftime("%b %d %Y %H:%M:%S", time.localtime(misc.now_UNIX()))
			plt.title('SCAN (' + self.label() + ')' + ' at ' + t0)
			plt.draw()

