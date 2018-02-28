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
# Example (bash): export PYTHONPATH=~/ruedi/python

import time

# import ruediPy classes:
from classes.temperaturesensor_MAXIM	import temperaturesensor_MAXIM
from classes.datafile					import datafile

TSENS		= temperaturesensor_MAXIM ( serialport = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller-if00-port0' , label = 'TEMP-TEST' )
# TSENS		= temperaturesensor_MAXIM ( serialport = '/dev/serial/by-id/usb-FTDI_TTL232R-3V3_FT9S6X3O-if00-port0' , label = 'TEMP-TEST' , fig_w = 8 , fig_h = 3)

# TSENS		= temperaturesensor_MAXIM ( serialport = '/dev/cu.usbserial' , label = 'TEMP-TEST' , fig_w = 8 , fig_h = 3)

DATAFILE	= datafile ( '~/data' )


# start data file:
DATAFILE.next() # start a new data file
print( 'Data output to ' + DATAFILE.name() )

# take temperature readings:
while 1:
	T,unit = TSENS.temperature(DATAFILE)
	print ( str(T) + ' ' + unit )
	TSENS.plot_tempbuffer()
