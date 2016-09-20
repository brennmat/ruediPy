# import general purpose Python classes:
import time
from datetime import datetime
import os
#havedisplay = "DISPLAY" in os.environ
#if havedisplay: # prepare plotting environment
#	import matplotlib
#	matplotlib.use('GTKAgg') # use this for faster plotting
#	import matplotlib.pyplot as plt

# import ruediPy classes:
from classes.rgams_SRS		import rgams_SRS
MS        = rgams_SRS ( serialport = '/dev/serial/by-id/usb-WuT_USB_Cable_2_WT2016234-if00-port0' , label = 'MS_MINIRUEDI_TEST', max_buffer_points = 1000 )
MS.filament_on() # turn on with default current
print 'Filament current: ' + MS.get_filament_current() + ' mA'

MS.set_RI(-9.5)
MS.set_RS(1080.0)
MS.tune_peak_position([4,14,18,28,32,40,44,84,86],[2.4,0.2,0.2,0.025,0.1,0.4,0.1,2.4,2.4],['M','F','F','F','F','F','M','M','M'],5)

input("Press ENTER to exit...")
