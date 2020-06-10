# Python script for testing the ruediPy code
# 
#
# Copyright 2020, Matthias Brennwald (brennmat@gmail.com)
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






############################################################################
### SCRIPT TO MEASURE BASIS SPECTRA FOR DECONVOLUTION OF NE-AR-H2O INTERFERENCE
############################################################################






# import general purpose Python classes:
import time

# import ruediPy classes:
from classes.rgams_SRS		import rgams_SRS
from classes.selectorvalve_VICI import selectorvalve_VICI
from classes.datafile		import datafile
from classes.misc		import misc


# set up analysis procedure:
MZ_F   = [(17,-7),(18,-8),(20,-10),(36,+1),(40,-3) , (28,-3) , (32,+5) ]
GATE_F = 1.0
N_F    = 20
MZ_M   = [(17,-7),(18,-8),(20,-10),(36,+1) ]
GATE_M = 1.0
N_M    = 20

# set up ruediPy objects:
MS = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2374683-if00-port0' , label = 'omanRUEDI', max_buffer_points = 500 , fig_w = 9 , fig_h = 10 )

DATAFILE  = datafile ( '/home/brennmat_deconv/data' )

# set/show MS configuraton:
MS.set_detector('F')
MS.set_electron_energy(45) # avoid Ar-40++ interference as much as possible, see Brennwald ES&T 2016
MS.filament_on() # turn on with default current
MS.print_status()

# set inlet selector valve:
VALVE = selectorvalve_VICI ( serialport = '/dev/serial/by-id/usb-FTDI_USB-RS232_Cable_FT1JKR1A-if00-port0', label = 'INLETSELECTOR' )

# prepare instrument
MS.set_detector('F')

for k in range(3):
# if False:

	DATAFILE.next(typ='MISC')
	print ('Data output to file ' + DATAFILE.name() )
	print ('\nMain readings (Faraday)...')
	MS.peak_zero_loop (MZ_F,'F',GATE_F,N_F,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)
	print ('\nMain readings (Multiplier)...')
	MS.peak_zero_loop (MZ_M,'M',GATE_M,N_M,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)

misc.wait_for_enter ('**** CLOSE INLET VALVE FOR BLANK -- PRESS ENTER ****')
misc.sleep(60)
for k in range(3):
	DATAFILE.next(typ='BLANK') # start a new data file, type 'BLANK'
	print ('Data output to file ' + DATAFILE.name() )
	print ('Data output to file ' + DATAFILE.name() )
	print ('\nMain readings (Faraday)...')
	MS.peak_zero_loop (MZ_F,'F',GATE_F,N_F,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)
	print ('\nMain readings (Multiplier)...')
	MS.peak_zero_loop (MZ_M,'M',GATE_M,N_M,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)

misc.wait_for_enter ('**** OPEN INLET VALVE AFTER BLANK -- PRESS ENTER ****')





print ( '...done.' )

# Wait to exit:
input ( "Press ENTER to exit..." )
