# MS_selectdetector.py
#
# Select which detector is used (Faraday electron Multiplier [SEM/CDEM])
#
# USAGE:
# >> python MS_selectdetector.py X
#
# X = F: send ion beam to Faraday detector, return command execution status
# X = M: send ion beam to SEM (electron Multiplier) detetctor, return command execution status
# X = ?: don't change anything and return current setting

from sys import argv
import MS_tools

# configure and open the serial connections (SRS RGA: 28'800 baud, 8 data bits, no parity, 2 stop bits)
ser = MS_tools.serialport ('/dev/ttyUSB4')

if argv[1] == 'F':
	out = MS_tools.cmdIO(ser,'HV0') # turn off SEM high voltage
elif argv[1] == 'M':
	out = MS_tools.cmdIO(ser,'HV*')
else:
	out = -1

print out

# clean up:
ser.close()
exit()