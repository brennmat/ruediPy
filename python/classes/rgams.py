# Code for the SRS RGA mass spec class

import serial
import time

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
		
		self.ser = ser;
		
	def param_IO(self,cmd):
		# set / read value of an operational parameter
		# cmd: command string that is sent to RGA (see RGA manual for commands and syntax)
		
		# send command to serial port:
		self.ser.write(cmd + '\r\n')
	
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
					ans = -1
			else:
				doWait = 0
				ans = ''
		
		# read back result:
		if ans != -1:
			while self.ser.inWaiting() > 0: # while there's something in the buffer...
				ans = ans + self.ser.read() # read each byte
	    
		# remove newline characters at the end and return the result:
		return ans.rstrip('\r\n')
