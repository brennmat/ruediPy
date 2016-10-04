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

# import ruediPy classes:
from classes.rgams_SRS		import rgams_SRS
from classes.datafile		import datafile

# set up ruediPy objects:
# MS        = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2016234-if00-port0' , label = 'MS_MINIRUEDI_TEST', max_buffer_points = 500 , fig_w = 13 , fig_h = 10 )
MS        = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2304868-if00-port0' , label = 'MS_MINIRUEDI_TEST', max_buffer_points = 500 , fig_w = 13 , fig_h = 10 )
#MS = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2374645-if00-port0' , label = 'MS_MINIRUEDI_TEST', max_buffer_points = 500 , fig_w = 13 , fig_h = 10 )
DATAFILE  = datafile ( '~/ruedi_data' )

# set/show MS configuraton:
has_multi = MS.has_multiplier();
if has_multi:
	print 'MS has electron multiplier installed.'
	# MS.set_multiplier_hv(1100)
	MS.set_detector('M')
	print 'Multiplier high voltage = ' + str(MS.get_multiplier_hv()) + ' V.'

else:
	print 'MS does not have electron multiplier installed.'
 
print 'MS max m/z range: ' + MS.mz_max()
print 'Ionizer electron energy: ' + MS.get_electron_energy() + ' eV'
MS.set_detector('F')
print 'Set ion beam to Faraday detector: ' + MS.get_detector()
MS.filament_on() # turn on with default current
print 'Filament current: ' + MS.get_filament_current() + ' mA'
#MS.set_electron_energy(60)  <-- uncomment this to change electon energy in ion source

# warm up instrument
n = 10
print 'Warming up instrument for ' + str(n) + ' seconds...'
MS.set_detector('F')
peak,unit = MS.peak(28,1,'nofile')
peak,unit = MS.peak(28,1,'nofile')
MS.peakbuffer_clear()
T0 = time.time() + n # n seconds from now
while time.time() < T0:
	peak,unit = MS.peak(28,1,'nofile')
	MS.plot_peakbuffer()

# tune peak positions:
print 'Tuning peak positions...'
## MS.set_RI(-9.7) # set start value
## MS.set_RS(1070.0) # set start value
# MS.tune_peak_position([4,14,18,28,32,40,44,84],[2.4,0.2,0.2,0.025,0.1,0.4,0.1,2.4],['M','F','F','F','F','F','F','M'],max_iter=5,max_delta_mz = 0.02)
# MS.tune_peak_position([14,18,28,32,40,44],[0.2,0.2,0.025,0.1,0.4,0.1],['F','F','F','F','F','F'],max_iter=5,max_delta_mz = 0.02)
MS.tune_peak_position( [ (14,0.2,'F') , (18,0.4,'F') , (28,0.2,'F') , (32,0.2,'F') , (40,0.4,'F') , (44,0.5,'F') , (84,2.4,'M') ] , max_iter=10 , max_delta_mz = 0.05 )
MS.set_detector('F') # make sure ion beam is on Faraday

# series of sinlge mass measurements ('PEAK' readings):
print 'Single mass measurements...'
MS.peakbuffer_clear() # clear peakbuffer (to start with fresh display)
gate = 0.025
mz = (28, 32, 40, 44)
j = 0
# while j < 3:
while 1:
	DATAFILE.next(typ='SAMPLE',samplename='Test_'+str(j)) # start a new data file, type 'SAMPLE'
	print 'Data output to ' + DATAFILE.name()
	k = 0
	while k < 10: # single peak readings
		k = k+1
		print 'Frame ' + str(k) + ':'
		for m in mz:
			peak,unit = MS.peak(m,gate,DATAFILE) # get PEAK value
			print '  mz=' + str(m) + ' peak=' + str(peak) + ' ' + unit # show PEAK value on console

		if k%5 == 0: # update trend plot every 5th iteration
			MS.plot_peakbuffer() # plot PEAK values in buffer (time trend)

	j = j+1

print '...done.'

# turn off filament:
MS.filament_off()
print 'Filament current: ' + MS.get_filament_current() + ' mA'

print '...all measurements done.'

# Wait to exit:
input("Press ENTER to exit...")
