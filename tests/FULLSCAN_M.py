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
# Copyright (C) 2016  Matthias Brennwald
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
import time
from datetime import datetime
import os
havedisplay = "DISPLAY" in os.environ
if havedisplay: # prepare plotting environment
	import matplotlib
	matplotlib.use('GTKAgg') # use this for faster plotting
	import matplotlib.pyplot as plt

# import ruediPy classes:
from classes.rgams		import rgams
from classes.selectorvalve	import selectorvalve
from classes.datafile	import datafile

# set up ruediPy objects:
MS        = rgams( serialport = '/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2016234-if00-port0' , label = 'MS_MINIRUEDI1', max_buffer_points = 1000 )
VALVE     = selectorvalve( serialport = '/dev/serial/by-id/pci-WuT_USB_Cable_2_WT2304832-if00-port0', label = 'INLETSELECTOR' )
DATAFILE  = datafile( '~/ruedi_data' )

# start data file:
DATAFILE.next() # start a new data file
print 'Data output to ' + DATAFILE.name()

VALVE.setpos(3,DATAFILE)
print 'Valve position is ' + str(VALVE.getpos())

# print some MS information:
print 'MS has electron multiplier: ' + MS.hasMultiplier()
print 'MS max m/z range: ' + MS.mzMax()

# change MS configuraton:
MS.setDetector('M')
print 'Set ion beam to Faraday detector: ' + MS.getDetector()
MS.filamentOn() # turn on with default current
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

# scan Ar-40 peak:
print 'Preparing scan (waiting for air inflow)... '
VALVE.setpos(3,DATAFILE)
time.sleep(10)
print 'Scanning...'
mz,intens,unit = MS.scan(1,200,25,2.4,DATAFILE)
MS.plot_scan (mz,intens,unit)
print '...done.'

# turn off filament:
MS.filamentOff()
print 'Filament current: ' + MS.getFilamentCurrent() + ' mA'

print '...done.'

# Wait to exit:
input("Press ENTER to exit...")
