# Python script for testing the ruediPy code: determine peak heights of pure gases for use as basis spectra for deconvolution
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

# import general purpose Python classes:
import time
#from datetime import datetime
#import os

# import ruediPy classes:
from classes.rgams_SRS		import rgams_SRS
from classes.datafile		import datafile
from classes.misc		import misc

# set up ruediPy objects:
MS = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2374683-if00-port0' , label = 'omanRUEDI', max_buffer_points = 500 , fig_w = 9 , fig_h = 10 )
DATAFILE  = datafile ( '/home/brennmat_deconv/data' )

# set/show MS configuraton:
MS.set_detector('F')
#MS.set_electron_energy(60)  <-- uncomment this to change electon energy in ion source
MS.filament_on() # turn on with default current
MS.print_status()

# prepare instrument
MS.set_detector('F')

mzF = [ (13,-4) , (14,-5) , (15,-6) , (16,-7) , (20,+3) , (28,-3) , (29,-4) , (32,+5) , (40,-3) , (44,+3) ];

# peak-height readings

DATAFILE.next(typ='SAMPLE',samplename='deconv_test') # start a new data file, type 'SAMPLE'
gateF = 2.4;
nF = round ( 15.0 / gateF );
print ('\nFaraday) readings...')
MS.peak_zero_loop (mzF,'F',gateF,nF,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)

DATAFILE.next(typ='SAMPLE',samplename='deconv_test') # start a new data file, type 'SAMPLE'
gateF = 1.0;
nF = round ( 24 / gateF );
print ('\nFaraday) readings...')
MS.peak_zero_loop (mzF,'F',gateF,nF,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)

DATAFILE.next(typ='SAMPLE',samplename='deconv_test') # start a new data file, type 'SAMPLE'
gateF = 0.1;
nF = round ( 24 / gateF );
print ('\nFaraday) readings...')
MS.peak_zero_loop (mzF,'F',gateF,nF,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)



print ( '...done.' )

# Wait to exit:
input ( "Press ENTER to exit..." )
