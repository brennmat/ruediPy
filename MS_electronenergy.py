# MS_electronenergy.py
#
# Set electron energy of ionizer, and return (new) electron energy value.
#
# USAGE:
# >> python MS_electronenergy.py X
#
# X = number: set electron energy to X eV, return command execution status
# X = '*': set electron energy to default value, return command execution status
# X = ?: don't change anything and return current setting

from sys import argv
import MS_tools

# configure and open the serial connections (SRS RGA: 28'800 baud, 8 data bits, no parity, 2 stop bits)
ser = MS_tools.serialport ('/dev/ttyUSB4')

# send  FL command for filament control to RGA, and read back response:
out = MS_tools.cmdIO(ser,'EE' + argv[1])

print out

# clean up:
ser.close()
exit()