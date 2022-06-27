# Python script for testing the ruediPy code
# 
#
# Copyright 2016, Matthias Brennwald (brennmat@gmail.com) and Yama Tomonaga
# 
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
# Copyright 2016, 2017, Matthias Brennwald (brennmat@gmail.com)
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


# make shure Python knows where to look for the RUEDI Python code
# http://stackoverflow.com/questions/4580101/python-add-pythonpath-during-command-line-module-run
# Example (bash): export PYTHONPATH=~/ruediPy/python

import time

# import ruediPy classes:
from classes.pressuresensor_WIKA	import pressuresensor_WIKA
from classes.datafile			import datafile

# for Linux (use device 'file' by ID to avoid confusion of com ports):
PSENS		= pressuresensor_WIKA ( serialport = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_57494B41_502D3358_2264352-if00-port0' , label = 'TOTALPRESSURE' , max_buffer_points = 500)


# for Mac OS X (use SiLabs USB driver):
# PSENS		= pressuresensor_WIKA ( serialport = '/dev/cu.SLAB_USBtoUART' , label = 'TOTALPRESSURE' )

DATAFILE	= datafile ( '~/data' )

# start data file:
DATAFILE.next() # start a new data file
print ( 'Data output to ' + DATAFILE.name() )

# take pressure readings:
while 1:
	p,unit = PSENS.pressure(DATAFILE)
	print ( str(p) + ' ' + unit )
	PSENS.plot_pressbuffer()
	time.sleep (2)
