# Code for the SRS RGA mass spec class

import serial
import time
import struct
import numpy
from classes.misc	import misc


class rgams:

	def __init__(self,P):
		# Initialize mass spectrometer (SRS RGA), configure serial port connection
		# P: device name of the serial port, e.g. P = '/dev/ttyUSB4'
	
		# open and configure serial port for communication with SRS RGA (28'800 baud, 8 data bits, no parity, 2 stop bits
		ser = serial.Serial(
			port     = P,
			baudrate = 28800,
			parity   = serial.PARITY_NONE,
			stopbits = serial.STOPBITS_TWO,
			bytesize = serial.EIGHTBITS,
			timeout  = 5.0
		)
		ser.flushInput() 	# make sure input is empty
		ser.flushOutput() 	# make sure output is empty
		
		self.ser = ser
	
	def warning(self,msg):
		# warn about issues related to operation of MS
		# msg: warning message
		misc.warnmessage ('SRS RGA',msg)
	
	def param_IO(self,cmd,ansreq):
		# set / read value of an operational parameter
		# cmd: command string that is sent to RGA (see RGA manual for commands and syntax)
		# ansreq: answer from RGA expected?
		#	ansreq = 1: answer expected, check for answer
		#	ansreq = 0: no answer expected, don't check for answer
		# result: answer code from RGA
		
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
					if t > 5: # give up waiting
						doWait = 0
						self.warning('could not determine parameter value or status (no response from RGA)')
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
			
		
	def setElectronEnergy(self,val):
		# set electron energy of the ionizer
		# val: electron energy in eV
				
		# send command to serial port:
		self.param_IO('EE' + str(val),1)

	def getElectronEnergy(self):
		# get electron energy of the ionizer (in eV)
				
		# send command to serial port:
		ans = self.param_IO('EE?',1)
		return ans

	def setFilamentCurrent(self,val):
		# set filament current
		# val: current in mA
				
		# send command to serial port:
		self.param_IO('FL' + str(val),1)

	def getFilamentCurrent(self):
		# get filament current (in eV)
				
		# send command to serial port:
		ans = self.param_IO('FL?',1)
		return ans

	def filamentOn(self):
		# turn on filament current at default value
				
		# send command to serial port:
		self.param_IO('FL*',1)

	def filamentOff(self):
		# turn off filament (set current to zero)
		self.setFilamentCurrent(0)

	def hasMultiplier(self):
		# check if MS has electron multiplier installed
		if hasattr(self, '_hasmulti') == 0: # never asked for multiplier before
			self._hasmulti = self.param_IO('MO?',1) # remember for next time
		return self._hasmulti

	def mzMax(self):
		# determine highest mz value available from MS
		if hasattr(self, '_mzmax') == 0: # never asked for mzMax before
			x = self.param_IO('MF?',1) # get current MF value
			self.param_IO('MF*',0) # set MF to default value, which equals M_MAX
			self._mzmax = self.param_IO('MF?',1) # read back M_MAX value
			self.param_IO('MF' + x,0) # set back to previous MF value
		return self._mzmax

	def setDetector(self,det):
		# tell RGA to direct the ion beam to the Faraday or electron Multiplier detector (SEM/CDEM)
		# det = 'F' --> Faraday
		# det = 'M' --> Multiplier

		# send command to serial port:		
		if det == 'F':
			self.param_IO('HV0',1)
		elif det == 'M':
			if self.hasMultiplier():
				self.param_IO('HV*',1)
			else:
				self.warning ('RGA has no electron multiplier installed!')
		else:
			self.warning ('Unknown detector ' + det)
				
	
	def scan(self,low,high,step):
		# analog scan
		# low: low m/z value
		# high: high m/z value
		# step: scan resolution (number of mass increment steps per amu)
		# 	step = integer number --> use given number (high number equals small mass increments between steps)
		# 	step = '*' use default value (step = 10)
		
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
		if high > self.mzMax():
			self.warning ('Scan must end at m/z=' + self.mzMax() + ' or lower! Ending at m/z= ' + self.mzMax + '...')
			low = self.mzMax()
		if low >= high:
			self.warning ('Scan m/z value at start must be lower than at end. Swapping values...')
			x = low;
			low = high;
			high = x;
		
		# configure scan:
		self.param_IO('MI' + str(low),0) # low end mz value
		self.param_IO('MF' + str(high),0) # high end mz value
		self.param_IO('SA' + str(step),0) # number of steps per amu
		N = self.param_IO('AP?',1) # number of data points in the scan
		N = int(N)
		
		# start the scan:
		self.ser.write('SC1\r\n')
		
		# read back result from RGA:
		Y = [] # init empty list
		k = 0
		nb = 0 # number of bytes read
		u = ''
		while ( k < N ): # read data points
			
			# wait for data in buffer:
			t = 0
			dt = 0.1
			doWait = 1
			while doWait > 0:
				if self.ser.inWaiting() == 0: # wait
					time.sleep(dt)
					t = t + dt
					if t > 5: # give up waiting
						doWait = -1
				else:
					doWait = 0
					
			# read back result:
			if doWait == -1:
				self.warning('RGA did not produce scan result (or took too long)!')
			else:
				# read byte and append to u:
				u = u + self.ser.read()
				nb = nb + 1
				if nb == 4: # all four bytes for next value read, parse data
					u = struct.unpack('<i',u)[0] # unpack 4-byte data value
					u = u * 1E-16 # divide by 1E-16 to convert to Amperes
					Y.append(u) # append value to list 'ans'
					
					# prepare for next value:
					k = k + 1
					u = ''
					nb = 0
		
		# flush the remaining data from the serial port buffer (total pressure measurement):
		time.sleep(0.5) # wait a little to get all the data into the buffer
		self.ser.flushInput() 	# make sure input is empty
		self.ser.flushOutput() 	# make sure output is empty

		
		M = numpy.linspace(low, high, N)
		unit = 'A'

		self.warning('SCANNING MAY NEED MORE TESTING!!!')
			
		return M,Y,unit
		
