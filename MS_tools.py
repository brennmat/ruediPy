# Helper functions for use with SRS RGA

import serial
import time

def serialport(P):
	# open and configure serial port for communication with SRS RGA (28'800 baud, 8 data bits, no parity, 2 stop bits)
	#
	# INPUT:
	# P = device name of the port, e.g. P = '/dev/ttyUSB4'
	# 
	# OUTPUT:
	# ser: serial port object for communication with SRS RGA
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
	
	return ser
	
		
def cmdIO(ser,cmd):
	# send a command to the serial port, and read back the result bytes (not full lines)
	#
	# INPUT:
	# ser: serial port object (as obtained from MS_tools.serialport(...))
	# cmd: command string
	#
	# OUTPUT:
	# ans: answer from SRS RGA
	
	# send command to serial port:
	ser.write(cmd + '\r\n')
	
	# wait for response
	t = 0
	dt = 0.1
	doWait = 1
	while doWait:
		if ser.inWaiting() == 0: # wait
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
		while ser.inWaiting() > 0: # while there's something in the buffer...
			ans = ans + ser.read() # read each byte

	# return the result:
	return ans
	
	
def cmdIO_line(ser,cmd):
	# send a command to the serial port, and read back the result (full lines)
	#
	# INPUT:
	# ser: serial port object (as obtained from MS_tools.serialport(...))
	# cmd: command string
	#
	# OUTPUT:
	# ans: answer from SRS RGA
	
	# send command to serial port:
	ser.write(cmd + '\r\n')
	
	# wait for response
	t = 0
	dt = 0.1
	doWait = 1
	while doWait:
		if ser.inWaiting() == 0: # wait
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
		while ser.inWaiting() > 0: # while there's something in the buffer...
			ans = ans + ser.readline() # read each line

	# return the result:
	return ans