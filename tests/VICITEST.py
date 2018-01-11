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

# import general purpose Python classes:

# import ruediPy classes:
from classes.selectorvalve_VICI	import selectorvalve_VICI
from classes.datafile		import datafile

# set up ruediPy objects:
VALVE     = selectorvalve_VICI ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2374672-if00-port0', label = 'INLETSELECTOR' )
DATAFILE  = datafile ( '~/data' )

# start data file:
DATAFILE.next() # start a new data file
print ( 'Data output to ' + DATAFILE.name() )

# change valve positions:
while True:
	VALVE.setpos(1,DATAFILE)
	print ( 'Valve position is ' + str(VALVE.getpos()) )
	VALVE.setpos(2,DATAFILE)
	print ( 'Valve position is ' + str(VALVE.getpos()) )
	VALVE.setpos(5,DATAFILE)
	print ( 'Valve position is ' + str(VALVE.getpos()) )
	VALVE.setpos(4,DATAFILE)
	print ( 'Valve position is ' + str(VALVE.getpos()) )
	VALVE.setpos(2,DATAFILE)
	print ( 'Valve position is ' + str(VALVE.getpos()) )
	VALVE.setpos(6,DATAFILE)
	print ( 'Valve position is ' + str(VALVE.getpos()) )
