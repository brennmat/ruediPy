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

# import general purpose Python classes:
import time
#from datetime import datetime
#import os

# import ruediPy classes:
from classes.rgams_SRS		import rgams_SRS
from classes.datafile		import datafile

# set up ruediPy objects:
MS = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2350188-if00-port0' , label = 'MS_MINIRUEDI_TEST', max_buffer_points = 500 , fig_w = 13 , fig_h = 10 )
DATAFILE = datafile ( '~/data' )

# set/show MS configuraton:
MS.set_detector('F')
#MS.set_electron_energy(60)  <-- uncomment this to change electon energy in ion source
MS.filament_on() # turn on with default current
MS.print_status()

# warm up instrument
n = 0
print ('Warming up instrument for ' + str(n) + ' seconds...')
MS.set_detector('F')
peak,unit = MS.peak(28,1,'nofile')
peak,unit = MS.peak(28,1,'nofile')
MS.peakbuffer_clear()
T0 = time.time() + n # n seconds from now
while time.time() < T0:
	peak,unit = MS.peak(28,1,'nofile')
	MS.plot_peakbuffer()


# 	MS.set_DI(114)

# tune peak positions:
print ('Tuning peak positions...')
## MS.set_RI(-9.7) # set start value
## MS.set_RS(1070.0) # set start value
MS.tune_peak_position( [ (14,1,0.2,'F') , (18,1,0.4,'F') , (28,1,0.2,'F') , (32,1,0.2,'F') , (40,1,0.4,'F') , (44,1,0.5,'F') , (84,0.65,2.4,'M') ] , max_iter=10 , max_delta_mz = 0.05 )
MS.set_detector('F') # make sure ion beam is on Faraday

# conditioning F:
for k in range(5):
	peak,unit = MS.peak(28,0.1,'nofile')

# series of sinlge mass measurements ('PEAK' readings):
print ('Single mass measurements...')
MS.peakbuffer_clear() # clear peakbuffer (to start with fresh display)
peaks = [ (32,0.5,'F') , (28,0.5,'F') , (40,0.5,'F') , (44,0.5,'F') , (84,2.4,'M') ]

peaks = [ (40,0.5,'F') ]

j = 0
# while j < 3:
while 1:
	DATAFILE.next(typ='SAMPLE',samplename='Test_'+str(j)) # start a new data file, type 'SAMPLE'
	print ( 'Data output to ' + DATAFILE.name() )
	k = 0
	while k < 50: # single peak readings
		k = k+1
		print ( 'Frame ' + str(k) + ':' )
		for p in peaks:
			MS.set_detector(p[2])
			peak,unit = MS.peak(p[0],p[1],DATAFILE) # get PEAK value
			print ( '  mz=' + str(p[0]) + ' detector=' + p[2] +' peak=' + str(peak) + ' ' + unit )  # show PEAK value on console

		MS.plot_peakbuffer() # plot PEAK values in buffer (time trend)

	j = j+1

print ( '...done.' )

# turn off filament:
MS.filament_off()
print ( 'Filament current: ' + MS.get_filament_current() + ' mA' )

print ( '...all measurements done.' )

# Wait to exit:
input ( "Press ENTER to exit..." )
