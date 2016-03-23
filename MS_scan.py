# MS_scan.py
#
# Scan across given mass range and return signal intensities
#
# INPUT and OUTPUT:
# input 1: initial mass (amu)
# input 2: final mass (amu)

# MS_filament.py
#
# Turn filament on or off, and return (new) filament current
#
# INPUT and OUTPUT:
# input = 0 turns filament off, returns status of command execution
# input = * turns filament on at default current setting, returns status of command execution
# arg = 1.1 sets filament current to 1.1 mA, returns status of command execution
# arg = ? don't change anything, return currently set filament current in mA
#
# OUTPUT:
# filament current (mA)

from sys import argv
import time
import serial
import MS_tools

# configure and open the serial connections (SRS RGA: 28'800 baud, 8 data bits, no parity, 2 stop bits)
ser = MS_tools.serialport ('/dev/ttyUSB4')

# format FL command for filament control:
cmd = 'FL' + argv[1]

# send command to RGA:
ser.write(cmd + '\r\n')

# wait for response:
t = 0
dt = 0.1
doWait = 1
while doWait:
	if ser.inWaiting() == 0: # wait
		time.sleep(dt)
		t = t + dt
		if t > 5: # give up waiting
			doWait = 0
			out = -1
	else:
		doWait = 0

# read back result:
if ser.inWaiting() > 0:
	out = ''
	while ser.inWaiting() > 0:
		out += ser.read(1)

# print result
print out

# clean up:
ser.close()
exit()