# make shure Python knows where to look for the RUEDI Python code
# http://stackoverflow.com/questions/4580101/python-add-pythonpath-during-command-line-module-run
# Example (bash): export PYTHONPATH=~/ruedi/python

# import ruediPy classes:
from classes.pressuresensor_WIKA	import pressuresensor_WIKA

PSENS	= pressuresensor_WIKA ( serialport = '/dev/serial/by-id/pci-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_57494B41_502D3358_2254391-if00-port0' , label = 'WIKA' )
while 1:
	p,unit = PSENS.pressure('nofile')
	print ( str(p) + ' ' + unit )
