# Helper functions for use with SRS RGA

import serial

def serialport(P):
	# open and configure serial port for communication with SRS RGA (28'800 baud, 8 data bits, no parity, 2 stop bits)
	# P = device name of the port, e.g. P = '/dev/ttyUSB4'
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