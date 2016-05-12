#!/usr/bin/env python
# Write/read procedure for RGA100/200/300 Residual Gas Analyzer
# Copyrigh 2016 Yama Tomonaga

import sys
import time
import serial
import struct

ser = serial.Serial(
	port='/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2304837-if00-port0',
	baudrate = 28800,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	rtscts=True,
	dsrdtr=True,
	timeout=10
	)
ser.flushInput()
rgaout=""
ser.write(str(sys.argv[1])+'\r')

if sys.argv[1] == 'SC1':
	i=1
	x=1
	while i<=int(sys.argv[2]):
		while x<=4:
			rgaout = rgaout + ser.read()
			x+=1
		print struct.unpack('<i',rgaout)[0]
		rgaout=""
		x=1
		i+=1
else:
	i=1
	while i<=int(sys.argv[2]):
		rgaout = ser.readline()
		print rgaout
		i+=1
