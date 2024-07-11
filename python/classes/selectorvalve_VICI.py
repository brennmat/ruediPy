# Code for the VICI selector valve class
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
	from pathlib import Path
	from classes.misc	import misc
except ImportError as e:
	print (e)
	raise

# check Python version and print warning if we're running version < 3:
if ( sys.version_info[0] < 3 ):
	warnings.warn("ruediPy / selectorvalve_VICI class is running on Python version < 3. Version 3.0 or newer is recommended!")


class selectorvalve_VICI:
	"""
	ruediPy class for VICI valve control. This assumes the serial protocol used with VICI's older "microlectric" actuators. For use with the newer "universal" actuators, they must be set to "legacy mode" using the "LG1" command (see page 8 of VICI document "Universal Electric Actuator Instruction Manual"). The self.set_legacy command may be useful for this.
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

			from pkg_resources import parse_version
			if parse_version(serial.__version__) >= parse_version('3.3') :
				# open port with exclusive access:
				ser = serial.Serial(
					port      = serialport,
					baudrate  = 9600,
					parity    = serial.PARITY_NONE,
					stopbits  = serial.STOPBITS_ONE,
					bytesize  = serial.EIGHTBITS,
					timeout   = 5.0,
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
					timeout  = 5.0
				)

			# make sure serial buffers are empty:
			ser.flushOutput()
			time.sleep(0.1)
			ser.flushInput()

			self.ser = ser;
			self._ser_locked = False

			# determine number of valve positions:
			self.get_serial_lock()
			self.ser.write('NP\r\n'.encode('ascii')) # send NP command to valve controller

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
						self.warning('could not determine number of valve postions (no response from valve)')
						ans = '-1'
				else:
					doWait = 0
					ans = ''
			
			# read back result:
			if (ans != '-1'):
				time.sleep(dt) # wait some more to be sure the valve response is transferred to the serial buffer completely
				while self.ser.inWaiting() > 0: # while there's something in the buffer...
					ans = ans + self.ser.read().decode('ascii') # read each byte

			try:
				ans = ans.split('=')[1] # split answer in the form 'NP = 6'
				ans = ans.strip() # strip away whitespace
			except:
				self.warning('could not parse response from valve: ans = ' + ans)
				ans = '?'
			
			self.release_serial_lock()
			
			# check result:
			if not ans.isdigit():
				self.warning('could not determine number of valve positions.')
				ans = '-1'

			# store number of positions:
			self._num_positions = int(ans)

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
		
		self.get_serial_lock()
		self.ser.write(('LG1\r\n').encode('ascii'))
		self.release_serial_lock()
		
		time.sleep(0.5)


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
		
		if val > self.getnumpos():
			self.warning( 'Cannot set valve position to ' + str(val) + ': number of valve positions = ' + str(self.getnumpos()) + '. Skipping...' )
		
		if val < 1:
			self.warning( 'Cannot set valve position to ' + str(val) + '. Skipping...' )
		else:
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
		
		# lock serial port:
		self.get_serial_lock()
		
		# make sure serial port buffer is empty:
		self.ser.flushInput()   #pot make sure input is empty
		self.ser.flushOutput()  # make sure output is empty

		# send command to serial port:
		self.ser.write('CP\r\n'.encode('ascii'))
		
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
					self.warning('could not determine valve position (no response from valve)')
					ans = '-1'
			else:
				doWait = 0
				ans = ''
		
		# read back result:
		if (ans != '-1'):
			time.sleep(dt) # wait some more to be sure the valve response is transferred to the serial buffer completely
			while self.ser.inWaiting() > 0: # while there's something in the buffer...
				ans = ans + self.ser.read().decode('ascii') # read each byte
		
		try:
			ans = ans.split('=')[1] # split answer in the form 'Position is = 1'
			ans = ans.strip() # strip away whitespace
		except:
			self.warning('could not parse response from valve: ans = ' + ans)
			ans = '?'
		
		# release serial port:
		self.release_serial_lock()

		# check result:
		if not ans.isdigit():
			self.warning('could not determine valve position (position = ' + ans + ')')
			ans = '-1'

		# return the result:
		return int(ans)


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

