# Code for the VICI selector valve class

import serial
import time

class selectorvalve:
	def __init__(self,P):
		# Initialize valve (VICI), configure serial port connection
		# P: device name of the serial port, e.g. P = '/dev/ttyUSB3'
	
		# open and configure serial port for communication with VICI valve (9600 baud, 8 data bits, no parity, 1 stop bit
		ser = serial.Serial(
			port     = P,
			baudrate = 9600,
			parity   = serial.PARITY_NONE,
			stopbits = serial.STOPBITS_ONE,
			bytesize = serial.EIGHTBITS,
			timeout  = 5.0
		)
		ser.flushInput() 	# make sure input is empty
		ser.flushOutput() 	# make sure output is empty
		
		self.ser = ser;
		
	def setpos(self,val):
		# set valve position
		# val: position
		
		# send command to serial port:
		self.ser.write('GO' + str(val) + '\r\n')
		
	def getpos(self):
		# get valve position
		
		# send command to serial port:
		self.ser.write('CP\r\n')
		
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
