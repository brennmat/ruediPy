# Code for the VICI selector valve class
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
	from pathlib import Path
	from .misc	import misc
except ImportError as e:
	print (e)
	raise

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / selectorvalve_VICI class is running on Python version < 3. Version 3.0 or newer is recommended!")


class selectorvalve_VICI:
	"""
	ruediPy class for VICI valve control. This assumes the serial protocol used with VICI's older "microlectric" actuators. Initialization sends the "LG1" command best-effort so universal actuators reply in the legacy dialect, then queries NP and raises if the position count is invalid. The set_legacy command can re-apply legacy mode after a controller reset.
	"""
	
	########################################################################################################
	
	
	def __init__( self , serialport , label = 'SELECTORVALVE' , statusfilepath = None ):
		'''
		selectorvalve_VICI.__init__( serialport , label = 'SELECTORVALVE' , statusfilepath = None )
		
		Initialize SELECTORVALVE object (VICI valve), configure serial port connection
		
		INPUT:
		serialport: device name of the serial port, e.g. P = '/dev/ttyUSB3'
		label (optional): label / name of the SELECTORVALVE object (string). Default: label = 'SELECTORVALVE'
		label (optional): label / name of the SELECTORVALVE object (string, will be used as the file name for the status file)
		statusfilepath (optional): path where the status file will be written (string). No files will be written if statusfilepath = None.

		OUTPUT:
		(none)
		'''

		self._label = label
			
		try:
			# open and configure serial port for communication with VICI valve (9600 baud, 8 data bits, no parity, 1 stop bit
			# use exclusive access mode if possible (available with serial module version 3.3 and later)

			try:
				# open port with exclusive access when supported by pyserial:
				ser = serial.Serial(
					port      = serialport,
					baudrate  = 9600,
					parity    = serial.PARITY_NONE,
					stopbits  = serial.STOPBITS_ONE,
					bytesize  = serial.EIGHTBITS,
					timeout   = 5.0,
					exclusive = True
				)
			except TypeError:
				# older pyserial: fallback without exclusive flag
				ser = serial.Serial(
					port     = serialport,
					baudrate = 9600,
					parity   = serial.PARITY_NONE,
					stopbits = serial.STOPBITS_ONE,
					bytesize = serial.EIGHTBITS,
					timeout  = 5.0
				)

			self.ser = ser;
			self._ser_locked = False

			self._flush_serial()
			self._enter_legacy_mode()
			self._flush_serial()

			raw = self._read_serial_response(
				'NP\r\n',
				'could not determine number of valve positions (no response from valve)'
			)
			numpos = self._parse_legacy_value(raw, 'number of valve positions')
			if numpos is None or numpos < 1:
				detail = ''
				if raw is not None:
					detail = '; ans = ' + raw
				raise RuntimeError(
					'Could not determine number of valve positions for ' + self.label() +
					' on ' + serialport + detail
				)

			self._num_positions = numpos

			self._statusfile = None
			if statusfilepath is not None:
				try:
					# create valve status file:
					if len(self._label) == 0:
						raise
					p = str(Path(statusfilepath,self._label+'.txt'))
					self._statusfile = open( p , "wt" )
					self.log( 'status file = ' + p )
					self.writestatusfile(None)
				except:
					self.warning( 'Could not set up status file for writing of valve position.' )
				
			u = 'Successfully configured VICI selector valve on ' + serialport + ', number of positions = ' + str(self._num_positions)
			if self._statusfile is not None:
				u = u + ', status file = ' + p		
			self.log( u )
			
		# Error handling:
		except Exception as e:
			self.warning( 'Could not initialise VICI selectorvalve:' + repr(e) )			
			raise e


	########################################################################################################
	

	def get_serial_lock(self):
		'''
		selectorvalve_VICI._get_serial_lock()
		
		Lock serial port for exclusive access (important if different threads / processes are trying to use the port). Make sure to release the lock after using the port (see selectorvalve_VICI._release_serial_lock()!
		
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
		selectorvalve_VICI._release_serial_lock()
		
		Release lock on serial port.
		
		INPUT:
		(none)
		
		OUTPUT:
		(none)
		'''

		# release the lock:
		self._ser_locked = False



	########################################################################################################



	def warning(self,msg):
		'''
		selectorvalve_VICI.warning(msg)
		
		Issue warning about issues related to operation of the valve.
		
		INPUT:
		msg: warning message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.warnmessage ('[' + self.label() + '] ' + msg)
		
	
########################################################################################################

	
	def log(self,msg):
		'''
		selectorvalve_VICI.log(msg)
		
		Issue log message related to operation of the valve.
		
		INPUT:
		msg: log message (string)
		
		OUTPUT:
		(none)
		'''
		
		misc.logmessage ('[' + self.label() + '] ' + msg)


	########################################################################################################
	

	def label(self):
		"""
		label = selectorvalve_VICI.label()

		Return label / name of the SELECTORVALVE object
		
		INPUT:
		(none)
		
		OUTPUT:
		label: label / name (string)
		"""
		
		try:
			label = self._label
		except:
			label = ''
		pass
		
		return label

	
	########################################################################################################
	

	def getnumpos(self):
		"""
		positions = selectorvalve_VICI.getnumpos()

		Return number of positions of the SELECTORVALVE object
		
		INPUT:
		(none)
		
		OUTPUT:
		positions: number of positions (int)
		"""
		
		return self._num_positions

	
	########################################################################################################
	
	

	def set_legacy(self):
		'''
		selectorvalve_VICI.set_legacy()

		Set communication protocol to LEGACY mode (useful to make the newer valve controlers compatible with the LEGACY protocol).

		INPUT:
		(none)

		OUTPUT:
		(none)
		'''
		
		self._enter_legacy_mode()
		self._flush_serial()


	########################################################################################################
	

	def setpos(self,val,f):
		'''
		selectorvalve_VICI.setpos(val,f)

		Set valve position

		INPUT:
		val: new valve position (integer)
		f: datafile object for writing data (see datafile.py). If f = 'nofile', data is not written to any data file.

		OUTPUT:
		(none)
		'''
		
		val = int(val)
		numpos = self.getnumpos()

		if numpos < 1:
			self.warning( 'Cannot set valve position to ' + str(val) + ': number of valve positions unknown (' + str(numpos) + '). Skipping...' )
			return

		if val < 1:
			self.warning( 'Cannot set valve position to ' + str(val) + '. Skipping...' )
			return

		if val > numpos:
			self.warning( 'Cannot set valve position to ' + str(val) + ': number of valve positions = ' + str(numpos) + '. Skipping...' )
			return

		curpos = self.getpos()
		if not curpos == val: # check if valve is already at desired position
			# send command to serial port:
			self.get_serial_lock()
			self.ser.write(('GO' + str(val) + '\r\n').encode('ascii'))
			self.release_serial_lock()
		
		# write to datafile
		if not f == 'nofile':
			f.write_valve_pos('SELECTORVALVE_VICI',self.label(),val,misc.now_UNIX())

		# give the valve some time to actually do the switch:
		time.sleep(0.5)
		
		# write valve position to status file:
		self.writestatusfile(val)


	########################################################################################################
	

	def getpos(self):
		'''
		pos = selectorvalve_VICI.getpos()

		Get valve position

		INPUT:
		(none)

		OUTPUT:
		pos: valve postion (integer)
		'''
		
		raw = self._read_serial_response(
			'CP\r\n',
			'could not determine valve position (no response from valve)'
		)
		val = self._parse_legacy_value(raw, 'valve position')
		if val is None:
			return -1

		return val


	########################################################################################################
	

	def _flush_serial(self):
		self.ser.flushOutput()
		time.sleep(0.1)
		self.ser.flushInput()


	########################################################################################################
	

	def _enter_legacy_mode(self):
		self.get_serial_lock()
		self.ser.write(('LG1\r\n').encode('ascii'))
		self.release_serial_lock()
		time.sleep(0.5)


	########################################################################################################
	

	def _read_serial_response(self, command, no_response_msg, timeout_s=5.0):
		self.get_serial_lock()
		self.ser.flushInput()
		self.ser.flushOutput()
		self.ser.write(command.encode('ascii'))

		t = 0
		dt = 0.1
		while self.ser.inWaiting() == 0:
			time.sleep(dt)
			t = t + dt
			if t > timeout_s:
				self.warning(no_response_msg)
				self.release_serial_lock()
				return None

		time.sleep(dt)
		ans = ''
		while self.ser.inWaiting() > 0:
			ans = ans + self.ser.read().decode('ascii')

		self.release_serial_lock()
		return ans


	########################################################################################################
	

	def _parse_legacy_value(self, raw, context):
		if raw is None:
			return None

		try:
			val = raw.split('=', 1)[1]
			val = val.strip()
		except IndexError:
			self.warning('could not parse response from valve: ans = ' + raw)
			return None

		if not val.isdigit():
			if context == 'number of valve positions':
				self.warning('could not determine number of valve positions.')
			else:
				self.warning('could not determine valve position (position = ' + val + ')')
			return None

		return int(val)


	########################################################################################################
	

	def writestatusfile(self,pos):
		if self._statusfile is not None:
			try:
				p = 'UNKNOWN'
				t = str(misc.now_UNIX()) # get current UNIX / Epoch time
				try:
					if pos > 0:
						p = str(pos)
				except:
					pass
				p = str(t) + ": POSITION = " + p
				self._statusfile.seek(0)   # clear the file
				self._statusfile.truncate()   # clear the file
				self._statusfile.write(p+'\n') # write valve position to file
				self._statusfile.flush()       # make sure data gets written to file now (don't wait for flushing file buffer)
				# time.sleep(0.05)
			except:
				self.warning('Could not write valve position to status file')

