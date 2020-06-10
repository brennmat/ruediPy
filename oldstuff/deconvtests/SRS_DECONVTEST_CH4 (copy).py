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

# import general purpose Python classes:
import time
#from datetime import datetime
#import os

# import ruediPy classes:
from classes.rgams_SRS		import rgams_SRS
from classes.datafile		import datafile
from classes.misc		import misc

# set up analysis procedure:
MZ_F_main   = [(15,-6),(28,-3),(32,+5),(40,-3),(44,3)] # m/z values used for quantification of gas species
MZ_F_help   = [(14,-5),(16,-7),(29,-4)] # m/z values of "helper" peaks, used for deconvolution only
GATE_F_main = 1.0 # gate time for main F readings
N_F_main    = 10 # number of main F readings
GATE_F_help = GATE_F_main # gate time for helper F readings
N_F_help    = 10 # number of helper F readings

# set up deconvolution block:
TARGET_MZ      = 15
TARGET_SPECIES = 'CH4'
DECONV_DET     = 'F'
BASIS          = ( ('CH4',14,0.103,15,0.806,16,1.0) , ('N2',14,0.059,15,0.00012,28,1.0,29,0.0065) , ('AIR',14,0.059,15,0.00014,16,0.0158,28,1.0,29,0.0065,32,0.208) )

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
n = 0
if n > 0:
	print ('Warming up instrument for ' + str(n) + ' seconds...')

# prepare readings
DATAFILE.next(typ='SAMPLE',samplename='deconv_test_CH4') # start a new data file, type 'SAMPLE'
gateF = 1;
## gateM = 1.0;

print ('Data output to file ' + DATAFILE.name() )

# peak-height readings for main analysis, followed by additional peak-height readings to help compensation of mass-spectrometric overlaps
print ('\nMain readings (Faraday)...')
MS.peak_zero_loop (MZ_F_main,'F',GATE_F_main,N_F_main,2,DATAFILE,clear_peakbuf_cond=True,clear_peakbuf_main=True)
print ('\nDeconv helper readings (Faraday)...')
MS.peak_zero_loop (MZ_F_help,'F',GATE_F_help,N_F_help,0,DATAFILE,clear_peakbuf_cond=False,clear_peakbuf_main=False)

# write deconvolution info to file (for CH4 on m/z=15):
MS.write_deconv_info(target_mz=TARGET_MZ,target_species=TARGET_SPECIES,deconv_detector=DECONV_DET,basis=BASIS,f=DATAFILE)

print ( '...done.' )

# Wait to exit:
input ( "Press ENTER to exit..." )
